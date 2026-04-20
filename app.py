from flask import Flask, jsonify, render_template

app = Flask(__name__)

database = {
    'students': [
        {"id": 1, "name": "samuel", "surname": "martis","personality": "in love","img": "http://www.gcm.sk/images/logo.jpg"},
        {"id": 2, "name": "andrej", "surname": "bucko","personality": "rasist","img": "http://www.gcm.sk/images/logo.jpg"},
        {"id": 3, "name": "rasto", "surname": "patak","personality": "shy","img": ""},
        {"id": 4, "name": "martin", "surname": "cepcek", "img": " "},
        {"id": 5, "name": "peter", "surname": "marcin", "img": " "},
        {"id": 6, "name": "janko", "surname": "kral", "img": " "},
        {"id": 7, "name": "lubo", "surname": "feldek", "img": " "},
        {"id": 8, "name": "ivan", "surname": "lesnik", "img": " "},
        {"id": 9, "name": "jozef", "surname": "mrkvicka", "img": " "},
        {"id": 10, "name": "michal", "surname": "kolar", "img": " "}
]}

@app.route('/students')
def list_students():
    return jsonify(database["students"])

@app.route('/students/<int:id>')
def find_student(id):
    student = database["students"][id - 1]
    return jsonify(student)
@app.route('/str')
def pusti_stranku():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json

    message = data.get("message")
    name = data.get("name")
    personality = data.get("personality")

    # 🔑 key pre pamäť
    key = name

    # 🧠 vytvor pamäť ak neexistuje
    if key not in memory:
        memory[key] = []

    try:
        # 🧠 system message
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

        # 🧠 pridaj históriu
        messages += memory[key]

        # 👤 aktuálna správa
        messages.append({
            "role": "user",
            "content": message
        })

        # 🤖 AI call
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages
        )

        reply = completion.choices[0].message.content

        # 💾 uloženie do pamäte
        memory[key].append({"role": "user", "content": message})
        memory[key].append({"role": "assistant", "content": reply})

        return jsonify({"reply": reply})

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == "__main__":
    app.run()

if __name__ == '__main__':
    app.run(debug=True)
