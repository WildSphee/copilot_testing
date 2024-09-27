from datetime import datetime

import pandas as pd

from llms.copilot import create_one_chat_compl


def generate_copilot_answers(input_csv_path: str, output_csv_dir: str):
    """
    Reads the input CSV file, generates answers using the copilot for each question,
    and saves the results to a new CSV file.

    Parameters:
    - input_csv_path (str): Path to the input CSV file ('testing_set.csv').
      The CSV should have the following columns:
        - 'question': The question to be answered.
        - 'luisgpt_answer': The ground truth answer (used for reference).

    - output_csv_dir (str): Directory where the output CSV file will be saved.
      The output file will be named 'copilot_result_<date_time>.csv'.

    The function generates copilot answers for each question and saves the
    question, copilot_answer, and luisgpt_answer to the output CSV.
    """

    df = pd.read_csv(input_csv_path)

    results = []

    # Loop through each row and generate copilot answers
    for index, row in df.iterrows():
        question = row["question"]
        luisGPT_answer = row["luisgpt_answer"]

        try:
            # Generate the copilot answer and get the response time
            copilot_answer, res_time = create_one_chat_compl(question)

            # Skip if the copilot answer is invalid
            if copilot_answer == "To clarify, did you mean:":
                print(f"Skipping row {index} due to invalid copilot answer.")
                continue

        except Exception as e:
            print(f"Error processing row {index}: {e}")
            copilot_answer = ""
            res_time = 0

        results.append(
            {
                "question": question,
                "copilot_answer": copilot_answer,
                "luisgpt_answer": luisGPT_answer,
                "response_time": res_time,
            }
        )
        print(f"Processed row {index}")

    # Create a new DataFrame with the results
    results_df = pd.DataFrame(results)

    # Get current date and time as a string
    date_str = datetime.now().strftime("%m_%d_%H%M")

    # Construct the output file path
    output_file_path = f"{output_csv_dir}/copilot_result_{date_str}.csv"

    # Save the results to a new CSV file
    results_df.to_csv(output_file_path, index=False)
    print(f"Results saved to {output_file_path}")
