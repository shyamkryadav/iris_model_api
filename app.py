import pandas as pd
from flask import Flask, request, jsonify
import pickle

app = Flask(__name__)

# Load the model and scaler
model = pickle.load(open("model.pkl", "rb"))
scaler = pickle.load(open("scaler.pkl", "rb"))

@app.route("/predict", methods=["POST"])
def predict():
    json_ = request.json
    query_df = pd.DataFrame(json_)
    query_df = scaler.transform(query_df)  # Scale the input data
    prediction = model.predict(query_df)
    return jsonify({"Prediction": list(prediction)})

if __name__ == "__main__":
    app.run(debug=True)
