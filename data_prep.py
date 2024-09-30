import os
from datetime import datetime
from typing import List

import docx
import pandas as pd
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter

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


def generate_context() -> List[List]:
    """
    Recursively reads all .docx and .pdf files in the 'context/' directory and its subdirectories,
    splits the text into sentences using RecursiveCharacterTextSplitter,
    and returns a list of lists where each inner list contains a single sentence.

    Returns:
        list_of_sentences (list): A list of lists, e.g.,
        [["First sentence of doc1."], ["Second sentence of doc1."], ..., ["Sentence from docN."]]
    """

    # Initialize the list to hold all sentences
    list_of_sentences = []

    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        separators=[".\n", ". ", ".", "!", "?", "\n\n", "\n", "。", "！", "？"],
        chunk_size=1000,
        chunk_overlap=0,
        length_function=len,
    )

    # Define the root directory
    root_directory = "context"

    # Walk through the directory recursively
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            print(f"{filename=}")
            if filename.lower().endswith(".docx"):
                # Read docx file
                try:
                    doc = docx.Document(filepath)
                    full_text = []
                    for para in doc.paragraphs:
                        full_text.append(para.text)
                    text = "\n".join(full_text)
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
                    continue
            elif filename.lower().endswith(".pdf"):
                # Read pdf file
                try:
                    text = ""
                    with open(filepath, "rb") as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page_num in range(len(pdf_reader.pages)):
                            page = pdf_reader.pages[page_num]
                            page_text = page.extract_text()
                            if page_text:
                                text += page_text
                except Exception as e:
                    print(f"Error reading {filepath}: {e}")
                    continue
            else:
                # Skip other files
                continue

            sentences = text_splitter.split_text(text)

            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:  # If sentence is not empty
                    list_of_sentences.append([sentence])

    return list_of_sentences
