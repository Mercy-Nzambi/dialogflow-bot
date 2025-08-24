from flask import Flask, request, jsonify
import csv
import difflib
import os

app = Flask(__name__)

# Load FAQ into dictionary
faq_data = {}

def load_faq(file_path="agriculture_faq.csv"):
    abs_path = os.path.abspath(file_path)
    print(f"Loading FAQ from: {abs_path}")
    try:
        with open(file_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                q = row["Question"].strip().lower()
                a = row["Answer"].strip()
                faq_data[q] = a
        print(f"✅ Loaded {len(faq_data)} FAQ entries")
    except Exception as e:
        print(f"⚠️ Could not load FAQ: {e}")

load_faq("agriculture_faq.csv")

def find_best_answer(user_input):
    if not user_input:
        return "I didn’t catch that, can you try again?"
    user_input = user_input.strip().lower()
    questions = list(faq_data.keys())
    match = difflib.get_close_matches(user_input, questions, n=1, cutoff=0.6)
    if match:
        return faq_data[match[0]]
    return "I'm not sure, but I'm still learning about that!"

@app.route("/webhook", methods=["POST"])
def webhook():
    req = request.get_json(force=True, silent=True)
    print("Incoming JSON:", req)  # Debugging log

    if not req:
        return jsonify({"fulfillmentText": "Sorry, I didn’t receive any input."})

    # Extract user input (Dialogflow ES format)
    user_input = req.get("queryResult", {}).get("queryText", "")

    # Find the best FAQ answer
    response_text = find_best_answer(user_input)

    # Respond to Dialogflow ES
    return jsonify({
        "fulfillmentText": response_text
    })

if __name__ == "__main__":
    app.run(debug=True, port=8080)
