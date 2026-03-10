import joblib

model = joblib.load("app/ml_model/model.pkl")
vectorizer = joblib.load("app/ml_model/vectorizer.pkl")

def predict_spam(text: str):
    transformed_text = vectorizer.transform([text])
    prediction = model.predict(transformed_text)[0]
    return "Spam" if prediction == 1 else "Not Spam"
