from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import pickle
from werkzeug.utils import secure_filename
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
import re
from langdetect import detect  # Import langdetect for language detection

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configure the upload folder and allowed extensions
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'images')  # Path to 'images' folder
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the 'images' folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Specify the Tesseract-OCR path
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'


# Function to classify the report using langdetect
def classify_text(text):
    language = detect(text)
    categories = {
        'Health': ['स्वास्थ्य', 'hospital', 'health', 'doctor', 'medicine', 'treatment'],
        'Communication': ['सञ्चार', 'communication', 'media', 'news', 'प्रसार'],
        'Tourism': ['पर्यटन', 'tourism', 'travel', 'भ्रमण', 'सफर'],
        'Development': ['विकास', 'development', 'infrastructure', 'शहरीकरण', 'आधारभूत', 'उद्यम'],
        'General': ['समाज', 'सामाजिक', 'समस्या', 'गुणवत्ता', 'समस्या'],
        'Education': ['शिक्षा', 'school', 'education', 'अधिकार', 'पढ्न', 'शिक्षक']
    }
    category_scores = {category: 0 for category in categories}
    for category, keywords in categories.items():
        for keyword in keywords:
            category_scores[category] += text.count(keyword)
    sorted_categories = sorted(category_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_categories[0][0] if sorted_categories[0][1] > 0 else 'General'


# Function to extract fields using regex
def extract_fields(text):
    postal = re.search(r'पत्र संख्या\s*[:|।]?\s*([A-Za-z0-9]+[-]?[A-Za-z0-9]*)', text)
    pradesh = re.search(r'प्रदेश\s*न\.?\s*\d+', text)
    title = re.search(r'विषय\s*[:|।]?\s*(.*?)\s*(?=\n|$)', text)
    desc = text[:300]
    date_nepali = re.search(r'मिति[:|।]?\s*(\d{4}\d{2}\d{2})', text)
    date_other = re.search(r'मिति[:|।]?\s*(\d{4}\d{2}\.\d{2})', text)
    date = date_nepali.group(1) if date_nepali else (date_other.group(1) if date_other else 'Not found')

    return {
        'postal': postal.group(1) if postal else 'Not found',
        'pradesh': pradesh.group() if pradesh else 'Not found',
        'title': title.group(1) if title else 'Not found',
        'date': date,
        'desc': desc
    }


# POST route for file upload
@app.route('/upload', methods=['POST'])
def fileUpload():
    if 'file' not in request.files:
        return jsonify({'message': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowedFile(file.filename):
        # Save the uploaded image to the 'images' folder
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Process the image with Tesseract OCR
        image = Image.open(file_path).convert('L')  # Convert to grayscale
        image = ImageEnhance.Contrast(image).enhance(2)  # Enhance contrast
        image = image.filter(ImageFilter.SHARPEN)  # Apply sharpening filter

        # Extract text using OCR (Nepali and English)
        extracted_text = pytesseract.image_to_string(image, lang='eng+nep')

        # Classify the report
        category = classify_text(extracted_text)

        # Extract fields from the text
        fields = extract_fields(extracted_text)

        # Save the extracted data and classification to a pickle file
        data = {
            'extracted_text': extracted_text,
            'category': category,
            'fields': fields
        }

        pickle_file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'extracted_data.pkl')
        with open(pickle_file_path, 'wb') as f:
            pickle.dump(data, f)

        return jsonify({
            'extracted_text': extracted_text,
            'category': category,
            'fields': fields
        })
    else:
        return jsonify({'message': 'Invalid file type'}), 400


if __name__ == "__main__":
    app.run(debug=True)
