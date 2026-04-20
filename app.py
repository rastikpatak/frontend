from flask import Flask, jsonify, render_template, request
from groq import Groq

app = Flask(__name__)

# 🔑 Groq client
client = Groq(api_key="YOUR_API_KEY_HERE")

# 🧠 memory storage
memory = {}

database = {
    'students': [
        {"id": 1, "name": "samuel", "surname": "martis","personality": "in love","img": "http://www.gcm.sk/images/logo.jpg"},
        {"id": 2, "name": "andrej", "surname": "bucko","personality": "rasist","img": "http://www.gcm.sk/images/logo.jpg"},
        {"id": 3, "name": "rasto", "surname": "patak","personality": "shy","img": ""},
        {"id": 4, "name": "martin", "surname": "cepcek", "img": " "},
    ]
}

@app.route('/students')
def list_students():
    return jsonify(database["students"])

@app.route('/chat', methods=["POST"])
def chat():
    data = request.json

    message = data.get("message")
    name = data.get("name")
    personality = data.get("personality")

    key = name

    if key not in memory:
        memory[key] = []

    try:
        messages = [
            {
                "role": "system",
                "content": f"""
You are a student named {name}.
Personality: {personality}.

Rules:
- Speak ONLY English
- Act like a real student
- Be short and natural
- Never say you are AI
"""
            }
        ]

        messages += memory[key]

        messages.append({
            "role": "user",
            "content": message
        })

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        reply = completion.choices[0].message.content

        memory[key].append({"role": "user", "content": message})
        memory[key].append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(debug=True)
