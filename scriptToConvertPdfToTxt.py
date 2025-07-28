# # Install Python libraries for OCR and PDF handling
# !pip install pytesseract pdf2image -q

# # Install system dependencies required by the libraries
# !apt-get update -q
# !apt-get install tesseract-ocr poppler-utils -q

import os
import re
import pytesseract
from pdf2image import convert_from_path
from tqdm import tqdm

def process_pdfs_to_txt(input_dir, output_dir):
    """
    Converts all PDFs in an input directory to cleaned .txt files in an output directory.

    The cleaning logic is as follows:
    1. Extracts text using OCR.
    2. Tries to find "Pathway Listings & Courses". If not found, falls back to finding "Home" (that is not "SCU Home").
    3. If both fail, it uses the start of the document.
    4. Finds the last occurrence of "Core Curriculum Sections" and removes all subsequent text.
    5. Keeps the text between these two markers.
    6. Saves the resulting text.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    print(f"Output will be saved to: '{os.path.abspath(output_dir)}'")

    # Get a list of all PDF files in the input directory
    try:
        pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith('.pdf')]
        if not pdf_files:
            print(f"Error: No PDF files found in the directory '{input_dir}'. Please check the path.")
            return
    except FileNotFoundError:
        print(f"Error: The input directory '{input_dir}' was not found.")
        return

    # Process each PDF file with a progress bar
    for filename in tqdm(pdf_files, desc="Converting PDFs"):
        pdf_path = os.path.join(input_dir, filename)
        txt_filename = os.path.splitext(filename)[0] + '.txt'
        txt_path = os.path.join(output_dir, txt_filename)

        try:
            # --- 1. OCR Extraction ---
            images = convert_from_path(pdf_path)
            raw_text = ""
            for img in images:
                raw_text += pytesseract.image_to_string(img) + "\n"

            if not raw_text.strip():
                print(f"\nWarning: No text could be extracted from '{filename}'. Skipping.")
                continue

            # --- 2. Text Processing ---
            # Define markers
            primary_start_marker = "Pathway Listings & Courses"
            fallback_start_marker = "Home"
            footer_marker = "Core Curriculum Sections"

            # Find the start index using primary marker first
            start_index = raw_text.find(primary_start_marker)

            # If primary marker is not found, use the fallback logic
            if start_index == -1:
                start_index = raw_text.find(fallback_start_marker)

            if start_index == -1:
                print(f"Using start of document.")
                start_index = 0 # Fallback to the very beginning of the document

            # Find the end index (last occurrence of the footer marker)
            end_index = raw_text.rfind(footer_marker)
            if end_index == -1:
                # If footer isn't found, take everything until the end of the text
                end_index = len(raw_text)

            # Slice the content
            core_content = raw_text[start_index:end_index]

            # --- 4. Save to File ---
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(core_content)

        except Exception as e:
            print(f"\nAn error occurred while processing '{filename}': {e}")

# --- Execution ---
# NOTE: Make sure your PDFs are in a folder named 'pdf' in the same
# directory as this script, or change the path accordingly.
input_directory = 'pdf'
output_directory = 'core-txt'

if not os.path.exists(input_directory):
    os.makedirs(input_directory)
    print(f"Created a dummy '{input_directory}' directory. Please upload your PDFs there.")

if not os.path.exists(output_directory):
    os.makedirs(output_directory)
    print(f"Created a dummy '{output_directory}' directory..")

# Run the conversion process
process_pdfs_to_txt(input_dir=input_directory, output_dir=output_directory)
print("\nConversion process complete.")
