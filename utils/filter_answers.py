import json

with open("regenerated_judgments_4.json") as f:
    judgements = json.load(f)

new_errors = []
for judgement in judgements:
    if "error" in judgement:
        new_errors.append(judgement)

with open("experiments/exp2_mt_bench/data/judgments/judgments_2.json") as f:
    judgements = json.load(f)

original_errors = []
for judgement in judgements:
    if "error" in judgement:
        original_errors.append(judgement)

print(f"{len(original_errors)=}, {len(new_errors)=}")

# with open("regenerated_answers.json") as f:
#     answers = json.load(f)

# dubious_answers = []
# for answer in answers:
#     answer_text = answer["answer_text"]
#     if "[ERROR: Failed to generate answer" in answer_text or answer_text == "":
#         dubious_answers.append(answer)

# print(f"{len(dubious_answers)=}")

# with open("non_dubious_answers.json") as f:
#     answers = json.load(f)

# non_dubious_answers = []
# for answer in answers:
#     answer_text = answer["answer_text"]
#     if (isinstance(answer_text, dict) and "error" in answer_text) or answer_text == "":
#         non_dubious_answers.append(answer)

# dubious_answer_ids = {a["answer_id"] for a in dubious_answers}
# non_dubious_answer_ids = {a["answer_id"] for a in non_dubious_answers}

# print(dubious_answer_ids.intersection(non_dubious_answer_ids))
