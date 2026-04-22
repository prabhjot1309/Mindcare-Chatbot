from flask import Flask, render_template, request, jsonify
from utils import analyze_text, predict_from_form

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("question")

    # Chat analysis
    risk = analyze_text(user_input)

    if risk == "HIGH":
        response = "You seem highly stressed. Consider talking to someone or a professional."
    elif risk == "MEDIUM":
        response = "You may be under stress. Try taking breaks and relaxing."
    else:
        response = "You seem okay. Keep maintaining balance."

    return jsonify({"answer": response})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    result = predict_from_form(
        int(data["age"]),
        data["gender"],
        data["family_history"],
        data["work_interfere"]
    )

    return jsonify({"result": result})


if __name__ == "__main__":
    app.run(debug=True)
