import time
from typing import Dict, Any
from anthropic import Anthropic
from openai import OpenAI
import google.generativeai as genai
import os


class ModelWrapper:
    def __init__(self, api_key: str, model_name: str, config: Dict[str, Any]):
        self.api_key = api_key
        self.model_name = model_name
        self.config = config
        self.timeout = config.get('generation', {}).get('timeout', 60)
    
    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError


class ClaudeWrapper(ModelWrapper):
    def __init__(self, api_key: str, model_name: str, config: Dict[str, Any]):
        super().__init__(api_key, model_name, config)
        self.client = Anthropic(api_key=api_key)
    
    def generate(self, prompt: str, **kwargs) -> str:
        temperature = kwargs.get('temperature', self.config.get('generation', {}).get('temperature', 0.7))
        max_tokens = kwargs.get('max_tokens', self.config.get('generation', {}).get('max_tokens', 2048))
        
        try:
            response = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except Exception as e:
            print(f"Error calling Claude API: {e}")
            raise


class GPTWrapper(ModelWrapper):
    def __init__(self, api_key: str, model_name: str, config: Dict[str, Any]):
        super().__init__(api_key, model_name, config)
        openai_models = config.get("models")["gpt"]
        self.use_openrouter_for_openai = all(
            openai_models[tier].startswith("openai/") for tier in openai_models
        )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1" if self.use_openrouter_for_openai else None
        )
    
    def generate(self, prompt: str, **kwargs) -> str:
        temperature = kwargs.get('temperature', self.config.get('generation', {}).get('temperature', 0.7))
        max_tokens = kwargs.get('max_tokens', self.config.get('generation', {}).get('max_tokens', 2048))
        
        try:
            kwargs = {
                "model": self.model_name, "messages": [{"role": "user", "content": prompt}],
                "extra_headers": {
                    "HTTP-Referer": "https://github.com/llm-bias-eval",
                    "X-Title": "LLM Bias Evaluation"
                },
            }
            if self.use_openrouter_for_openai:
                kwargs.update({"max_tokens": max_tokens})
            else:
                kwargs.update({"max_completion_tokens": max_tokens})

            if "gpt-5" not in self.model_name:
                # GPT-5 models don't support temperature.
                kwargs.update({"temperature": temperature})
            
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling GPT via OpenRouter: {e}")
            raise


class GeminiWrapper(ModelWrapper):
    def __init__(self, api_key: str, model_name: str, config: Dict[str, Any]):
        super().__init__(api_key, model_name, config)
        genai.configure(api_key=api_key)
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        
        self.model = genai.GenerativeModel(
            model_name,
            safety_settings=safety_settings
        )
    
    def generate(self, prompt: str, **kwargs) -> str:
        temperature = kwargs.get('temperature', self.config.get('generation', {}).get('temperature', 0.7))
        max_tokens = kwargs.get('max_tokens', self.config.get('generation', {}).get('max_tokens', 2048))
        
        generation_config = genai.GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
        )
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            if response.candidates and response.candidates[0].content.parts:
                return response.candidates[0].content.parts[0].text
            elif hasattr(response, 'text'):
                return response.text
            else:
                raise ValueError(f"Empty response. Finish reason: {response.candidates[0].finish_reason if response.candidates else 'No candidates'}")
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            raise


class OpenRouterWrapper(ModelWrapper):
    def __init__(self, api_key: str, model_name: str, config: Dict[str, Any]):
        super().__init__(api_key, model_name, config)
        
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )
    
    def generate(self, prompt: str, **kwargs) -> str:
        temperature = kwargs.get('temperature', self.config.get('generation', {}).get('temperature', 0.7))
        max_tokens = kwargs.get('max_tokens', self.config.get('generation', {}).get('max_tokens', 2048))
        retries = kwargs.get('retries', 3)
        
        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant. Always respond with valid JSON only, no markdown formatting."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                result = response.choices[0].message.content
                if result and len(result.strip()) > 10:
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
    VALID_VENDORS = ('claude', 'gpt', 'gemini')
    VALID_TIERS = ('fast', 'thinking')
    VENDOR_WRAPPERS = {
        'claude': ('ANTHROPIC_API_KEY', 'anthropic', ClaudeWrapper),
        'gpt': ('OPENROUTER_API_KEY', 'openrouter', GPTWrapper),
    }

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_keys = config.get('api_keys', {})
        self.models_config = config.get('models', {})

    def _get_api_key(self, env_var: str, config_key: str) -> str:
        return os.environ.get(env_var) or self.api_keys.get(config_key)

    def get_model(self, vendor: str, tier: str) -> ModelWrapper:
        vendor = vendor.lower()
        tier = tier.lower()
        
        if vendor not in self.VALID_VENDORS:
            raise ValueError(f"Unknown vendor: {vendor}")
        
        if tier not in self.VALID_TIERS:
            raise ValueError(f"Unknown tier: {tier}")
        
        if vendor in self.VENDOR_WRAPPERS:
            env_var, key_name, wrapper_cls = self.VENDOR_WRAPPERS[vendor]
            api_key = self._get_api_key(env_var, key_name)
            if vendor in self.models_config and tier in self.models_config[vendor]:
                model_name = self.models_config[vendor][tier]
                return wrapper_cls(api_key, model_name, self.config)
        
        if "gemini" in self.models_config:
            if tier in self.models_config['gemini']:
                model_name = self.models_config['gemini'][tier]
                if model_name.startswith('google/'):
                    api_key = self._get_api_key('OPENROUTER_API_KEY', 'openrouter')
                    return OpenRouterWrapper(api_key, model_name, self.config)
                api_key = self._get_api_key('GOOGLE_API_KEY', 'google')
                return GeminiWrapper(api_key, model_name, self.config)
    
    def get_all_models(self) -> Dict[str, ModelWrapper]:
        models = {}
        for vendor in ['claude', 'gpt', 'gemini']:
            for tier in ['fast', 'thinking']:
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
