from flask import Flask, request, render_template, send_file
import os
import PyPDF2
from deep_translator import GoogleTranslator

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
TXT_FOLDER = 'txt_files'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(TXT_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.pdf'):
            pdf_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(pdf_path)
            text = extract_text_from_pdf(pdf_path)
            try:
                # Split text into smaller chunks for translation
                text_chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
                translated_chunks = []
                for chunk in text_chunks:
                    try:
                        translated_chunk = GoogleTranslator(source='auto', target='nl').translate(chunk)
                        translated_chunks.append(translated_chunk)
                    except Exception as e:
                        return f"An error occurred during translation of chunk: {str(e)}", 500
                translated_text = ' '.join(translated_chunks)
            except Exception as e:
                return f"An error occurred during translation: {str(e)}", 500
            txt_filename = file.filename.replace('.pdf', '.txt')
            txt_path = os.path.join(TXT_FOLDER, txt_filename)
            with open(txt_path, 'w') as txt_file:
                txt_file.write(translated_text)
            return send_file(txt_path, as_attachment=True)
    return render_template('upload.html')

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

if __name__ == '__main__':
    app.run(debug=True)