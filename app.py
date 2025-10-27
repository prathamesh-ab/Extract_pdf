# # from flask import Flask, render_template, request, send_file
# # import os
# # import camelot
# # import pandas as pd

# # app = Flask(__name__)
# # UPLOAD_FOLDER = "uploads"
# # os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# # @app.route('/')
# # def index():
# #     return render_template('index.html')


# # @app.route('/extract', methods=['POST'])
# # def extract():
# #     if 'pdf_file' not in request.files:
# #         return "No file uploaded", 400

# #     file = request.files['pdf_file']
# #     if file.filename == '':
# #         return "No selected file", 400

# #     pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
# #     file.save(pdf_path)

# #     excel_path = os.path.join(UPLOAD_FOLDER, file.filename.replace('.pdf', '.xlsx'))

# #     try:
# #         # Try extracting tables using both modes
# #         tables_lattice = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
# #         tables_stream = camelot.read_pdf(pdf_path, pages='all', flavor='stream')

# #         all_tables = []
# #         if len(tables_lattice) > 0:
# #             all_tables.extend(tables_lattice)
# #         if len(tables_stream) > 0:
# #             all_tables.extend(tables_stream)

# #         if not all_tables:
# #             return "No tables found in the PDF.", 400

# #         # Combine all tables into one DataFrame
# #         df_combined = pd.DataFrame()
# #         for table in all_tables:
# #             df = table.df
# #             df_combined = pd.concat([df_combined, df, pd.DataFrame([[]])], ignore_index=True)

# #         # Save into a single Excel sheet
# #         df_combined.to_excel(excel_path, index=False, header=False, sheet_name='All_Tables')

# #         return send_file(excel_path, as_attachment=True)

# #     except Exception as e:
# #         return f"Error while processing: {str(e)}", 500


# # if __name__ == '__main__':
# #     app.run(debug=True)

# from flask import Flask, render_template, request, send_file
# import os
# import camelot
# import pandas as pd
# import zipfile
# from io import BytesIO

# app = Flask(__name__)

# UPLOAD_FOLDER = "uploads"
# OUTPUT_FOLDER = "outputs"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# @app.route('/')
# def index():
#     return render_template('index.html')


# @app.route('/extract', methods=['POST'])
# def extract():
#     if 'pdf_file' not in request.files:
#         return "No file uploaded", 400

#     file = request.files['pdf_file']
#     if file.filename == '':
#         return "No selected file", 400

#     pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
#     file.save(pdf_path)

#     excel_path = os.path.join(OUTPUT_FOLDER, file.filename.replace('.pdf', '.xlsx'))

#     try:
#         process_pdf(pdf_path, excel_path)
#         return send_file(excel_path, as_attachment=True)

#     except Exception as e:
#         return f"Error while processing: {str(e)}", 500


# @app.route('/batch_process', methods=['POST'])
# def batch_process():
#     """
#     Process all PDF files in the uploads directory and output them to the outputs directory.
#     Then return a ZIP of all results.
#     """
#     try:
#         pdf_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith('.pdf')]

#         if not pdf_files:
#             return "No PDF files found in uploads directory.", 400

#         for pdf_file in pdf_files:
#             pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file)
#             excel_path = os.path.join(OUTPUT_FOLDER, pdf_file.replace('.pdf', '.xlsx'))
#             process_pdf(pdf_path, excel_path)

#         # Create a ZIP file of all processed Excel files
#         zip_buffer = BytesIO()
#         with zipfile.ZipFile(zip_buffer, "w") as zipf:
#             for file_name in os.listdir(OUTPUT_FOLDER):
#                 file_path = os.path.join(OUTPUT_FOLDER, file_name)
#                 zipf.write(file_path, arcname=file_name)
#         zip_buffer.seek(0)

#         return send_file(
#             zip_buffer,
#             mimetype='application/zip',
#             as_attachment=True,
#             download_name='processed_excels.zip'
#         )

#     except Exception as e:
#         return f"Batch processing failed: {str(e)}", 500


# def process_pdf(pdf_path, excel_path):
#     """Extract tables from a single PDF and save to Excel."""
#     tables_lattice = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
#     tables_stream = camelot.read_pdf(pdf_path, pages='all', flavor='stream')

#     all_tables = []
#     if len(tables_lattice) > 0:
#         all_tables.extend(tables_lattice)
#     if len(tables_stream) > 0:
#         all_tables.extend(tables_stream)

#     if not all_tables:
#         raise ValueError(f"No tables found in {os.path.basename(pdf_path)}")

#     df_combined = pd.DataFrame()
#     for table in all_tables:
#         df = table.df
#         df_combined = pd.concat([df_combined, df, pd.DataFrame([[]])], ignore_index=True)

#     df_combined.to_excel(excel_path, index=False, header=False, sheet_name='All_Tables')


# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Flask, render_template, request, send_file
import os
import camelot
import pandas as pd
import zipfile
from io import BytesIO
import time  # ⏱️ Added for time tracking

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/extract', methods=['POST'])
def extract():
    if 'pdf_file' not in request.files:
        return "No file uploaded", 400

    file = request.files['pdf_file']
    if file.filename == '':
        return "No selected file", 400

    pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(pdf_path)

    excel_path = os.path.join(OUTPUT_FOLDER, file.filename.replace('.pdf', '.xlsx'))

    try:
        start_time = time.time()
        process_pdf(pdf_path, excel_path)
        end_time = time.time()
        print(f"✅ Processed single file '{file.filename}' in {end_time - start_time:.2f} seconds")
        return send_file(excel_path, as_attachment=True)

    except Exception as e:
        return f"Error while processing: {str(e)}", 500


@app.route('/batch_process', methods=['POST'])
def batch_process():
    """
    Process all PDF files in the uploads directory and output them to the outputs directory.
    Then return a ZIP of all results.
    """
    try:
        pdf_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith('.pdf')]

        if not pdf_files:
            return "No PDF files found in uploads directory.", 400

        print(f"🟢 Starting batch processing for {len(pdf_files)} PDF(s)...")
        batch_start = time.time()

        for pdf_file in pdf_files:
            file_start = time.time()
            pdf_path = os.path.join(UPLOAD_FOLDER, pdf_file)
            excel_path = os.path.join(OUTPUT_FOLDER, pdf_file.replace('.pdf', '.xlsx'))
            process_pdf(pdf_path, excel_path)
            file_end = time.time()
            print(f"📄 Processed '{pdf_file}' in {file_end - file_start:.2f} seconds")

        batch_end = time.time()
        total_time = batch_end - batch_start
        print(f"🏁 All {len(pdf_files)} PDF(s) processed in {total_time:.2f} seconds")

        # Create ZIP of all Excel outputs
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for file_name in os.listdir(OUTPUT_FOLDER):
                file_path = os.path.join(OUTPUT_FOLDER, file_name)
                zipf.write(file_path, arcname=file_name)
        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='processed_excels.zip'
        )

    except Exception as e:
        return f"Batch processing failed: {str(e)}", 500


def process_pdf(pdf_path, excel_path):
    """Extract tables from a single PDF and save to Excel."""
    tables_lattice = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    tables_stream = camelot.read_pdf(pdf_path, pages='all', flavor='stream')

    all_tables = []
    if len(tables_lattice) > 0:
        all_tables.extend(tables_lattice)
    if len(tables_stream) > 0:
        all_tables.extend(tables_stream)

    if not all_tables:
        raise ValueError(f"No tables found in {os.path.basename(pdf_path)}")

    df_combined = pd.DataFrame()
    for table in all_tables:
        df = table.df
        df_combined = pd.concat([df_combined, df, pd.DataFrame([[]])], ignore_index=True)

    df_combined.to_excel(excel_path, index=False, header=False, sheet_name='All_Tables')


if __name__ == '__main__':
    app.run(debug=True)
