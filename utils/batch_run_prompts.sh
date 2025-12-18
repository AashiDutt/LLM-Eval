CONFIG=config_mt_bench_sayak.yaml
VENDOR=gemini

run() {
  python utils/run_prompt.py \
    --config $CONFIG \
    --vendor $VENDOR \
    "$@"
}

# Claude Fast
run --prompts experiments/exp2_mt_bench/prompts.json --tier fast
run --prompts experiments/exp2_mt_bench/data/answers/answers.json --tier fast --use-response-model

# Claude Thinking
run --prompts experiments/exp2_mt_bench/prompts.json --tier thinking
run --prompts experiments/exp2_mt_bench/data/answers/answers.json --tier thinking --use-response-model
