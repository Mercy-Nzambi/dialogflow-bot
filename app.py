from flask import Flask, request, jsonify
import csv
import difflib
import os
import requests

app = Flask(__name__)

# -------------------------------
# Load FAQ from CSV (for webhook)
# -------------------------------
faq_data = {}

def load_faq(file_path="agriculture_faq_kids.csv"):
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            question = row["question"].strip().lower()
            answer = row["answer"].strip()
            faq_data[question] = answer
    print(f"✅ Loaded {len(faq_data)} FAQ entries")

load_faq()

def find_best_answer(user_input):
    user_input = user_input.strip().lower()
    questions = list(faq_data.keys())
    match = difflib.get_close_matches(user_input, questions, n=1, cutoff=0.6)
    if match:
        return faq_data[match[0]]
    else:
        return "I'm not sure, but I'm still learning about that!"

# -------------------------------
# Route 1: Webhook (Dialogflow calls this)
# -------------------------------
@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(silent=True, force=True) or {}
    user_input = (
        req.get("queryResult", {}).get("queryText", "")
        or req.get("text", "")
        or req.get("sessionInfo", {}).get("parameters", {}).get("any", "")
    )

    response_text = find_best_answer(user_input)

    return jsonify({
        "fulfillment_response": {
            "messages": [
                {
                    "text": {"text": [response_text]}
                }
            ]
        }
    })

# -------------------------------
# Route 2: Proxy (Unity calls this)
# -------------------------------
@app.route("/dialogflow", methods=["POST"])
def dialogflow_proxy():
    data = request.get_json(force=True)
    user_message = data.get("message", "")
    session_id = data.get("sessionId", "unity-session")

    if not user_message:
        return jsonify({"reply": "No message received."})

    # Instead of hitting webhook, we use FAQ logic for now
    response_text = find_best_answer(user_message)

    return jsonify({"reply": response_text})

# -------------------------------
# Run locally
# -------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
