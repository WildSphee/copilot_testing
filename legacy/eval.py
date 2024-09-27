import json
from datetime import datetime
from typing import Tuple

import pandas as pd

from llms.copilot import create_one_chat_compl
from llms.openai import call_openai


def eval_line(question, luisGPT_res) -> Tuple[str, str, float]:
    copilot_res, res_time = create_one_chat_compl(question)

    eval_prompt = f"""You are evaluating the results from two different bots based on various metrics. Please provide a detailed evaluation in JSON format for each metric, bot2 is not always correct, rate it base on how effective it answers the question - out of 10:

### Question:
{question}

### Copilot Result:
{copilot_res}

### Bot2 Result:
{luisGPT_res}

###### Evaluate only Copilot based on the following metrics and provide your exact output like below:
```
{{
    "faithfulness": {{
        "rating": 8,
        "reason": "Copilot accurately reflects the information provided in the source."
    }},
    "factualness": {{
        "rating": 7,
        "reason": "Copilot provides mostly accurate information but with minor errors."
    }},
    "clarity": {{
        "rating": 9,
        "reason": "Copilot presents information in a clear and understandable manner."
    }},
    "relevance": {{
        "rating": 6,
        "reason": "Copilot includes some irrelevant details."
    }},
    "conciseness": {{
        "rating": 8,
        "reason": "Copilot provides a concise summary of the information."
    }},
    "overall": {{
        "rating": 10,
        "reason": "Copilot delivers a great answer with room for improvement."
    }}
}}
```
Your output:
```
"""
    return copilot_res, call_openai(eval_prompt), res_time


df = pd.read_csv("testing_set.csv")

results = []


# Loop through each row and evaluate
for index, row in df.iterrows():
    question = row["question"]
    luisGPT_answer = row["luisgpt_answer"]

    try:
        copilot_answer, evaluation, response_time = eval_line(question, luisGPT_answer)
        evaluation = evaluation.strip("'```json\n").rstrip("\n```")
        print(f"trying to load 1st: {evaluation=}")
        eval_data = json.loads(evaluation)
    except (json.JSONDecodeError, KeyError, Exception) as e:
        print(f"Error processing row {index}: {e}")
        try:
            # Retry once
            copilot_answer, evaluation, response_time = eval_line(
                question, luisGPT_answer
            )
            evaluation = evaluation.strip("'```json\n").rstrip("\n```")
            print(f"trying to load 2nd: {evaluation=}")
            eval_data = json.loads(evaluation)
        except Exception:
            eval_data = {
                "faithfulness": {"rating": 0, "reason": 0},
                "factualness": {"rating": 0, "reason": 0},
                "clarity": {"rating": 0, "reason": 0},
                "relevance": {"rating": 0, "reason": 0},
                "conciseness": {"rating": 0, "reason": 0},
                "overall": {"rating": 0, "reason": 0},
            }
            response_time = 0

    results.append(
        {
            "Question": question,
            "copilot_answer": copilot_answer,
            "luisgpt_answer": luisGPT_answer,
            "response_time": response_time,
            "faithfulness_rating": eval_data.get("faithfulness", {}).get("rating"),
            "faithfulness_reason": eval_data.get("faithfulness", {}).get("reason"),
            "factualness_rating": eval_data.get("factualness", {}).get("rating"),
            "factualness_reason": eval_data.get("factualness", {}).get("reason"),
            "clarity_rating": eval_data.get("clarity", {}).get("rating"),
            "clarity_reason": eval_data.get("clarity", {}).get("reason"),
            "relevance_rating": eval_data.get("relevance", {}).get("rating"),
            "relevance_reason": eval_data.get("relevance", {}).get("reason"),
            "conciseness_rating": eval_data.get("conciseness", {}).get("rating"),
            "conciseness_reason": eval_data.get("conciseness", {}).get("reason"),
            "overall_rating": eval_data.get("overall", {}).get("rating"),
            "overall_reason": eval_data.get("overall", {}).get("reason"),
        }
    )
    print(f"Evaluating row {index}, result: {eval_data}")

# Create a new DataFrame with the results
results_df = pd.DataFrame(results)
results_df = results_df[results_df["copilot_answer"] != "To clarify, did you mean:"]


# get date time as str
date_str = datetime.now().strftime("%m_%d_%H%M")

# Save the results to a new CSV file
results_df.to_csv(f"results/evaluation_results_{date_str}.csv", index=False)
