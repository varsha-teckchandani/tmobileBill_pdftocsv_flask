import pdfplumber
import re
import sys
from typing import Tuple, Dict, List
from decimal import Decimal
from collections import defaultdict
import csv
from io import StringIO
from flask import Flask, render_template, request, redirect, url_for, send_file
import os

app = Flask(__name__)
# Folder to save uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions (you can modify this as needed)
ALLOWED_EXTENSIONS = {'pdf'}

# Check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return redirect(request.url)
    files = request.files.getlist('files')

    # Save files to the server
    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filename)
            saved_files.append(filename)

    # Call your Python script here to process the files
    output_csv = process_files(saved_files)

    return send_file(output_csv, as_attachment=True, download_name="processed_files.csv", mimetype='text/csv')

def extract_phone_bill_from_pdf(pdf_file: str) -> Tuple[Decimal, Dict[str, Decimal], str]:
    """
    Extract phone bill data from a PDF file.

    Args:
        pdf_file (str): Path to the PDF file

    Returns:
        Tuple[Decimal, Dict[str, Decimal], str]: (account_total, line_wise_extras, bill_period)
    """
    # Compile regex pattern once
    bill_period_pattern = re.compile(r"\b[A-Za-z]{3} \d{1,2} - [A-Za-z]{3} \d{1,2}\b")

    account_total = Decimal('0')
    bill_period = ""
    line_wise_extras = defaultdict(Decimal)

    try:
        with pdfplumber.open(pdf_file) as pdf:
            text = pdf.pages[1].extract_text()

            if not text:
                return account_total, dict(line_wise_extras), bill_period

            lines = [line for line in map(str.strip, text.split("\n")) if line]

            for line in lines:
                if line.startswith("Charged") and not bill_period:
                    if match := bill_period_pattern.search(line):
                        bill_period = match.group(0)
                        if account_total != 0:
                            break

                elif line.startswith("Account") and not account_total:
                    if parts := line.split(maxsplit=2):
                        try:
                            account_total = Decimal(parts[1].strip().replace("$", ""))
                            if bill_period:
                                break
                        except (IndexError, ValueError):
                            continue

                elif line.startswith("("):
                    key = line[:14]
                    try:
                        value = Decimal(line.rpartition("-")[-1].split(maxsplit=1)[0].strip().replace("$", ""))
                        line_wise_extras[key] = value
                    except (ValueError, IndexError):
                        continue

    except Exception as e:
        print(f"Error processing PDF {pdf_file}: {e}", file=sys.stderr)
        return account_total, dict(line_wise_extras), bill_period

    return account_total, dict(line_wise_extras), bill_period

def generate_csv(files: List[str]) -> str:
    """
    Generate CSV content from multiple PDF files.

    Args:
        files (List[str]): List of PDF file paths

    Returns:
        str: CSV formatted string
    """
    output_file_path = os.path.join("outputs", 'processed_output.csv')
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Line", "Bill Period", "Base charge", "Extra charges (Equipment, Services etc)", "Bill Amount"])

    for pdf_file in files:
        with open(pdf_file, 'r') as f:
            account_total, line_wise_extras, bill_period = extract_phone_bill_from_pdf(pdf_file)

            if line_wise_extras:
                base_cost_per_line = account_total / len(line_wise_extras)
                for line, extra in line_wise_extras.items():
                    total = extra + base_cost_per_line
                    writer.writerow([line, bill_period, f"${base_cost_per_line:.2f}", f"${extra:.2f}", f"${total:.2f}"])

    output_file_path = os.path.join("outputs", 'processed_output.csv')
    with open(output_file_path, 'w') as file:
        file.write(output.getvalue())

    # Optionally, you can close the StringIO object when done
    output.close()

    return output_file_path

def process_files(files):
    return generate_csv(files)

if __name__ == '__main__':
    # Ensure the upload folder exists
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)