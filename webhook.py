from flask import Flask, request, jsonify
import csv
import random

app = Flask(__name__)

# Load Q&A knowledge base from CSV
knowledge_base = {}
with open("agriculture_faq.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        knowledge_base[row["question"].strip().lower()] = row["answer"].strip()


# --- Route for Dialogflow ES Webhook ---
knowledge_base = {}

with open("knowledge_base.csv", newline='', encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        q = row.get("question") or row.get("Question")
        a = row.get("answer") or row.get("Answer")
        if q and a:  # only add if both exist
            knowledge_base[q.strip().lower()] = a.strip()



# --- Route for Unity Direct Call ---
@app.route('/dialogflow', methods=['POST'])
def dialogflow_unity():
    req = request.get_json(force=True)
    user_input = req.get("message", "").strip().lower()

    # Find answer from knowledge base
    reply = knowledge_base.get(user_input, "Sorry, I don't know the answer to that yet.")

    return jsonify({
        "reply": reply
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
