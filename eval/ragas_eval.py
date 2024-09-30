import os

import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    answer_relevancy,
    context_precision,
    context_recall,
    faithfulness,
)


def evaluate_with_ragas(input_csv_path, output_csv_path, contexts):
    """
    Evaluates answers using the RAGAS library and writes the evaluation results to a CSV file.

    Parameters:
    - input_csv_path (str): Path to the input CSV file containing the test data.
      The CSV should have the following columns:
        - 'question': The user's question.
        - 'copilot_answer': The answer generated by the model to be evaluated.
        - 'luisgpt_answer': The ground truth answer (used as context and ground truth).

    - output_csv_path (str): Path where the evaluation results CSV will be saved.
    - contexts: (List[List]): all files within the context/ folder

    The function reads the input CSV, performs evaluation using RAGAS metrics,
    and writes the results to the output CSV.
    """

    if "OPENAI_API_KEY" not in os.environ:
        raise ValueError(
            "Please set your OpenAI API key in the environment variable 'OPENAI_API_KEY'."
        )

    df = pd.read_csv(input_csv_path)

    # Filter out rows where 'copilot_answer' is invalid or missing
    df = df[
        df["copilot_answer"].notnull()
        & (df["copilot_answer"] != "To clarify, did you mean:")
    ]

    # Ensure required columns are present
    required_columns = {"question", "copilot_answer", "luisgpt_answer"}
    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"The input CSV must contain the following columns: {required_columns}"
        )

    # Prepare the data for RAGAS evaluation
    questions = df["question"].tolist()
    answers = df["copilot_answer"].tolist()
    ground_truths = df["luisgpt_answer"].tolist()

    # Create a HuggingFace Dataset
    data_dict = {
        "question": questions,
        "answer": answers,
        "ground_truth": ground_truths,
        "contexts": contexts,
    }

    eval_dataset = Dataset.from_dict(data_dict)

    # Evaluate using RAGAS
    result = evaluate(
        eval_dataset,
        metrics=[
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        ],
    )

    # Convert the evaluation results to a pandas DataFrame
    results_df = result.to_pandas()

    # Merge the evaluation results with the original data (optional)
    results_df = pd.concat([df.reset_index(drop=True), results_df], axis=1)

    # Save the results to a CSV file
    results_df.to_csv(output_csv_path, index=False)

    print(f"Evaluation completed. Results saved to {output_csv_path}")
