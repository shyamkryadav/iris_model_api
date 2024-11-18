import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import pickle

app = Flask(__name__)  # Use __name__ instead of _name_
CORS(app, resources={r"/predict": {"origins": "http://localhost:4200"}})  # Limit CORS to a specific origin

# Load the model and scaler
model = pickle.load(open("model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

@app.route("/predict", methods=["POST"])
def predict():
    try:
        json_ = request.json
        if not isinstance(json_, list):  # Ensure input is a list
            json_ = [json_]  # If not a list, wrap it in a list
        
        query_df = pd.DataFrame(json_)  # Create DataFrame from input data
        query_df = scaler.transform(query_df)  # Scale the input data
        prediction = model.predict(query_df)  # Make prediction
        return jsonify({"Prediction": list(prediction)})  # Return prediction as JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error message in response



# Add a GET route for testing
@app.route("/test", methods=["GET"])
def test():
    return jsonify({"message": "Flask app is working!"})  # Simple response for testing

if __name__ == "__main__":  # Correct __name__ here
    app.run(debug=True)
