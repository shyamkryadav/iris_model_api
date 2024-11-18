from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
# CORS(app, resources={r"/predict": {"origins": "http://localhost:4200"}})
# CORS(app, resources={
#     r"/predict": {"origins": "http://localhost:4200"},
#     r"/upload": {"origins": "http://localhost:4200"}
# })


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load the model and scaler
model = pickle.load(open("model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

# Configure the upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowedFile(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# POST route for file upload
@app.route('/upload', methods=['POST', 'GET'])
def fileUpload():
    if request.method == 'POST':
        files = request.files.getlist('files')
        if not files:
            return jsonify({'message': 'No files found'}), 400
        
        responses = []
        for f in files:
            filename = secure_filename(f.filename)
            if allowedFile(filename):
                try:
                    f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    responses.append({"name": filename, "status": "success"})
                except Exception as e:
                    responses.append({"name": filename, "status": "error", "error": str(e)})
            else:
                responses.append({"name": filename, "status": "error", "message": "File type not allowed"})
        
        return jsonify(responses)
    else:
        return jsonify({"status": "Upload API GET Request Running"})

# GET route for testing
@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "Flask app is working!"})

if __name__ == "__main__":
    app.run(debug=True)
