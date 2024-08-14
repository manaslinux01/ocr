
from flask import Flask, request
import requests
import easyocr
from pdf2image import convert_from_path
import os
import tempfile

app = Flask(__name__)

@app.route('/')
def index():
    try:
        url = request.args.get('url')
        if not url:
            return 'URL not found'

        response = requests.get(url)
        if response.status_code == 200:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_pdf:
                temp_pdf.write(response.content)
                temp_pdf_path = temp_pdf.name

            reader = easyocr.Reader(['en'],gpu = False)
            images = convert_from_path(temp_pdf_path)
            pdftext = ''

            with tempfile.TemporaryDirectory() as output_dir:
                for i, image in enumerate(images):
                    image_path = os.path.join(output_dir, f'page_{i + 1}.png')
                    image.save(image_path, 'PNG')
                    result = reader.readtext(image_path)
                    for (bbox, text, prob) in result:
                        pdftext += text + " "

            os.remove(temp_pdf_path)  # Clean up the temporary PDF file

            return pdftext.strip()

        else:
            return "Failed to download the PDF."

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)
