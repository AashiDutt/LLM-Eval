import os
import time
from typing import Any, Type
import json
import google.genai as genai
from anthropic import Anthropic
from openai import OpenAI
from pydantic import BaseModel


class ModelWrapper:
    def __init__(self, api_key: str, model_name: str, config: dict[str, Any]):
        self.api_key = api_key
        self.model_name = model_name
        self.config = config
        self.timeout = config.get("generation", {}).get("timeout", 60)

    def generate(
        self, prompt: str, system_prompt: str = None, response_model: Type[BaseModel] = None, **kwargs
    ) -> Any:
        raise NotImplementedError

    @staticmethod
    def _patch_json_schema_for_openai(schema: dict[str, Any]) -> dict[str, Any]:
        """
        Recursively patch JSON schema for OpenAI/OpenRouter strict mode:
        - Add additionalProperties: false to all object schemas
        - Remove description from $ref properties (OpenAI doesn't allow it)
        """
        if isinstance(schema, dict):
            schema = schema.copy()

            if "$ref" in schema:
                if "description" in schema:
                    schema.pop("description")

            if schema.get("type") == "object" and "additionalProperties" not in schema:
                schema["additionalProperties"] = False

            if "$defs" in schema:
                schema["$defs"] = {
                    def_name: ModelWrapper._patch_json_schema_for_openai(def_schema)
                    for def_name, def_schema in schema["$defs"].items()
                }

            if "properties" in schema:
                schema["properties"] = {
                    prop_name: ModelWrapper._patch_json_schema_for_openai(prop_schema)
                    for prop_name, prop_schema in schema["properties"].items()
                }

            for key, value in schema.items():
                if key not in ("additionalProperties", "$defs", "properties", "$ref", "description"):
                    schema[key] = ModelWrapper._patch_json_schema_for_openai(value)

        elif isinstance(schema, list):
            schema = [ModelWrapper._patch_json_schema_for_openai(item) for item in schema]

        return schema

    @staticmethod
    def _coerce_structured_response(
        payload: Any,
        response_model: Type[BaseModel],
    ) -> str:
        if response_model is None:
            return payload if isinstance(payload, str) else str(payload)

        try:
            # ---- validation only ----
            if isinstance(payload, response_model):
                pass
            elif isinstance(payload, BaseModel):
                response_model.model_validate(payload.model_dump())
            elif isinstance(payload, dict):
                response_model.model_validate(payload)
            elif isinstance(payload, str):
                response_model.model_validate_json(payload)
            else:
                raise ValueError(f"Unsupported structured payload type: {type(payload)}")

            # ---- success: always return string ----
            if isinstance(payload, BaseModel):
                return payload.model_dump_json()
            if isinstance(payload, dict):
                return json.dumps(payload)
            return payload if isinstance(payload, str) else str(payload)

        except Exception:
            # ---- failure: propagate ----
            raise


class ClaudeWrapper(ModelWrapper):
    # https://platform.claude.com/docs/en/build-with-claude/structured-outputs
    STRUCTURED_OUTPUTS_BETA = ["structured-outputs-2025-11-13"]

    def __init__(self, api_key: str, model_name: str, config: dict[str, Any]):
        super().__init__(api_key, model_name, config)
        self.client = Anthropic(api_key=api_key)

    def generate(
        self, prompt: str, system_prompt: str = None, response_model: Type[BaseModel] = None, **kwargs
    ) -> Any:
        temperature = kwargs.get("temperature", self.config.get("generation", {}).get("temperature", 0.7))
        max_tokens = kwargs.get("max_tokens", self.config.get("generation", {}).get("max_tokens", 2048))

        kwargs = {
            "model": self.model_name,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt is not None:
            kwargs["system"] = system_prompt
        try:
            if response_model is not None:
                try:
                    kwargs.update({"betas": self.STRUCTURED_OUTPUTS_BETA, "output_format": response_model})
                    response = self.client.beta.messages.parse(**kwargs)
                    return self._coerce_structured_response(response.parsed_output, response_model)
                except Exception as structured_error:
                    print(f"Structured Claude output failed ({self.model_name}): {structured_error}")
                    raise

            response = self.client.messages.create(**kwargs)
            result = response.content[0].text
            return result
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            raise


class GPTWrapper(ModelWrapper):
    def __init__(self, api_key: str, model_name: str, config: dict[str, Any]):
        super().__init__(api_key, model_name, config)
        openai_models = config.get("models")["gpt"]
        self.use_openrouter_for_openai = all(openai_models[tier].startswith("openai/") for tier in openai_models)

        self.client = OpenAI(
            api_key=api_key, base_url="https://openrouter.ai/api/v1" if self.use_openrouter_for_openai else None
        )

    @staticmethod
    def _build_messages(system_prompt: str, prompt: str) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _call_native_openai(
        self, messages: list[dict[str, str]], temperature: float, max_tokens: int, response_model: Type[BaseModel]
    ) -> Any:
        is_gpt5 = "gpt-5" in self.model_name
        request_kwargs = {"model": self.model_name, "messages": messages}
        if not is_gpt5:
            request_kwargs["temperature"] = temperature

        if response_model is not None:
            try:
                request_kwargs["max_output_tokens"] = max_tokens
                request_kwargs["text_format"] = response_model
                request_kwargs["input"] = request_kwargs.pop("messages")
                response = self.client.responses.parse(**request_kwargs)
                return self._coerce_structured_response(response.output_parsed, response_model)
            except Exception as structured_error:
                print(f"Structured OpenAI output failed ({self.model_name}): {structured_error}")
                raise

        request_kwargs["max_completion_tokens"] = max_tokens
        response = self.client.chat.completions.create(**request_kwargs)
        message_content = response.choices[0].message.content
        if isinstance(message_content, list):
            text = "".join(getattr(part, "text", "") for part in message_content)
        else:
            text = message_content or ""
        return text

    def generate(
        self, prompt: str, system_prompt: str = None, response_model: Type[BaseModel] = None, **kwargs
    ) -> Any:
        temperature = kwargs.get("temperature", self.config.get("generation", {}).get("temperature", 0.7))
        max_tokens = kwargs.get("max_tokens", self.config.get("generation", {}).get("max_tokens", 2048))
        messages = self._build_messages(system_prompt, prompt)

        if not self.use_openrouter_for_openai:
            return self._call_native_openai(messages, temperature, max_tokens, response_model)

        try:
            request_kwargs = {
                "model": self.model_name,
                "messages": messages,
                "extra_headers": {
                    "HTTP-Referer": "https://github.com/llm-bias-eval",
                    "X-Title": "LLM Bias Evaluation",
                },
            }
            request_kwargs.update({"max_tokens": max_tokens})

            if "gpt-5" not in self.model_name:
                # GPT-5 models don't support temperature.
                request_kwargs.update({"temperature": temperature})
            if response_model is not None:
                raw_schema = response_model.model_json_schema()
                patched_schema = self._patch_json_schema_for_openai(raw_schema)
                request_kwargs["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": response_model.__name__,
                        "schema": patched_schema,
                        "strict": True,
                    },
                }

            response = self.client.chat.completions.create(**request_kwargs)
            message_content = response.choices[0].message.content
            if isinstance(message_content, list):
                text = "".join(getattr(part, "text", "") for part in message_content)
            else:
                text = message_content or ""
            if response_model is not None:
                return self._coerce_structured_response(text, response_model)
            return text
        except Exception as e:
            print(f"Error calling GPT via OpenRouter: {e}")
            raise


class GeminiWrapper(ModelWrapper):
    def __init__(self, api_key: str, model_name: str, config: dict[str, Any]):
        super().__init__(api_key, model_name, config)

        self.safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        response_model: Type[BaseModel] = None,
        **kwargs,
    ) -> Any:
        temperature = kwargs.get("temperature", self.config.get("generation", {}).get("temperature", 0.7))
        max_tokens = kwargs.get("max_tokens", self.config.get("generation", {}).get("max_tokens", 2048))

        config = self._build_gen_config(
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            response_model=response_model,
        )

        try:
            if response_model is None:
                # plain text path
                resp = self._call(prompt, config)
                return self._extract_text_or_raise(resp)

            # structured path (+ optional repair retry)
            return self._generate_structured_with_optional_repair(
                prompt=prompt,
                config=config,
                response_model=response_model,
            )

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise

    def _build_gen_config(
        self,
        *,
        system_prompt: str = None,
        temperature: float,
        max_tokens: int,
        response_model: Type[BaseModel] = None,
    ) -> genai.types.GenerateContentConfig:
        cfg: dict[str, Any] = {
            "system_instruction": system_prompt,
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "safety_settings": self.safety_settings,
            # Uncomment to see magic ✨
            # "thinking_config": {"return_thoughts": True, "thinking_budget": 0}
        }
        if response_model is not None:
            cfg["response_mime_type"] = "application/json"
            cfg["response_json_schema"] = response_model.model_json_schema()
        return genai.types.GenerateContentConfig(**cfg)

    def _call(self, prompt: str, config: genai.types.GenerateContentConfig):
        return self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )

    def _extract_text_or_raise(self, response) -> str:
        text = getattr(response, "text", None)
        if text:
            return text

        # fallback: first candidate part
        candidates = getattr(response, "candidates", None)
        if candidates and candidates[0].content.parts:
            part_text = getattr(candidates[0].content.parts[0], "text", None)
            if part_text:
                return part_text

        finish_reason = candidates[0].finish_reason if candidates else "No candidates"
        raise ValueError(f"Empty response. Finish reason: {finish_reason}")

    def _generate_structured_with_optional_repair(
        self,
        *,
        prompt: str,
        config: genai.types.GenerateContentConfig,
        response_model: Type[BaseModel],
    ) -> Any:
        # Attempt 1: normal
        resp = self._call(prompt, config)
        text = self._extract_text_or_raise(resp)

        try:
            return self._coerce_structured_response(text, response_model)
        except Exception:
            # Only do the repair retry for flash models (your current behavior)
            if "flash" not in self.model_name:
                raise

            # Attempt 2: repair retry
            repair_prompt = (
                "Your previous output was invalid or did not match the schema. "
                "Return ONLY the JSON object that matches the schema. No extra text."
            )
            resp2 = self._call(repair_prompt + "\n\n" + prompt, config)
            text2 = self._extract_text_or_raise(resp2)
            return self._coerce_structured_response(text2, response_model)


class OpenRouterWrapper(ModelWrapper):
    def __init__(self, api_key: str, model_name: str, config: dict[str, Any]):
        super().__init__(api_key, model_name, config)

        self.client = OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

    def generate(
        self, prompt: str, system_prompt: str = None, response_model: Type[BaseModel] = None, **kwargs
    ) -> Any:
        temperature = kwargs.get("temperature", self.config.get("generation", {}).get("temperature", 0.7))
        max_tokens = kwargs.get("max_tokens", self.config.get("generation", {}).get("max_tokens", 2048))
        retries = kwargs.get("retries", 3)
        system_message = (
            system_prompt
            or "You are a helpful assistant. Always respond with valid JSON only, no markdown formatting."
        )
        response_format = None
        if response_model is not None:
            raw_schema = response_model.model_json_schema()
            patched_schema = self._patch_json_schema_for_openai(raw_schema)
            response_format = {
                "type": "json_schema",
                "json_schema": {
                    "name": response_model.__name__,
                    "schema": patched_schema,
                    "strict": True,
                },
            }
        base_payload = {
            "model": self.model_name,
            "messages": [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            base_payload["response_format"] = response_format

        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(**base_payload)
                message_content = response.choices[0].message.content
                if isinstance(message_content, list):
                    result = "".join(getattr(part, "text", "") for part in message_content)
                else:
                    result = message_content or ""
                if result and len(result.strip()) > 10:
                    if response_model is not None:
                        return self._coerce_structured_response(result, response_model)
                    return result
                if attempt < retries - 1:
                    print(f"  Retry {attempt + 1}: Empty or short response")
                    time.sleep(1)
            except Exception as e:
                if attempt < retries - 1:
                    print(f"  Retry {attempt + 1}: {e}")
                    time.sleep(2)
                else:
                    print(f"Error calling OpenRouter ({self.model_name}): {e}")
                    raise
        raise ValueError(f"Failed after {retries} attempts")


class ModelFactory:
    VALID_VENDORS = ("claude", "gpt", "gemini")
    VALID_TIERS = ("fast", "thinking")
    VENDOR_WRAPPERS = {
        "claude": ("ANTHROPIC_API_KEY", "anthropic", ClaudeWrapper),
        "gpt": ("OPENROUTER_API_KEY", "openrouter", GPTWrapper),
    }

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.api_keys = config.get("api_keys", {})
        self.models_config = config.get("models", {})

    def _get_api_key(self, env_var: str, config_key: str) -> str:
        return os.environ.get(env_var) or self.api_keys.get(config_key)

    def get_model(self, vendor: str, tier: str, model_name_override: str = None) -> ModelWrapper:
        vendor = vendor.lower()
        tier = tier.lower()

        if vendor not in self.VALID_VENDORS:
            raise ValueError(f"Unknown vendor: {vendor}")

        if tier not in self.VALID_TIERS:
            raise ValueError(f"Unknown tier: {tier}")

        if vendor in self.VENDOR_WRAPPERS:
            env_var, key_name, wrapper_cls = self.VENDOR_WRAPPERS[vendor]
            api_key = self._get_api_key(env_var, key_name)
            vendor_models = self.models_config.get(vendor, {})
            model_name = model_name_override or vendor_models.get(tier)
            if not model_name:
                raise KeyError(f"Missing model config for {vendor}.{tier}")
            return wrapper_cls(api_key, model_name, self.config)

        gemini_models = self.models_config.get("gemini", {})
        model_name = model_name_override or gemini_models.get(tier)
        if not model_name:
            raise KeyError(f"Missing model config for gemini.{tier}")
        if model_name.startswith("google/"):
            api_key = self._get_api_key("OPENROUTER_API_KEY", "openrouter")
            return OpenRouterWrapper(api_key, model_name, self.config)
        api_key = self._get_api_key("GOOGLE_API_KEY", "google")
        return GeminiWrapper(api_key, model_name, self.config)

    def get_all_models(self) -> dict[str, ModelWrapper]:
        models = {}
        for vendor in ["claude", "gpt", "gemini"]:
            for tier in ["fast", "thinking"]:
                key = f"{vendor}_{tier}"
                models[key] = self.get_model(vendor, tier)
        return models


def test_model(wrapper: ModelWrapper, test_prompt: str = "Hello! Please respond with 'API working'.") -> bool:
    try:
        response = wrapper.generate(test_prompt)
        if response and len(response) > 0:
            print(f"✓ {wrapper.model_name} working")
            return True
        else:
            print(f"✗ {wrapper.model_name} returned empty response")
            return False
    except Exception as e:
        print(f"✗ {wrapper.model_name} failed: {e}")
        return False
