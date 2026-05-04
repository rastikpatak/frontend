from flask import Flask, jsonify, request
from groq import Groq
import psycopg2
import os

app = Flask(__name__)

# 🔑 API key (lepšie cez ENV)
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# 🧠 memory (zatiaľ v RAM)
memory = {}

# 🗄️ PostgreSQL pripojenie
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="your_db_name",
        user="your_user",
        password="your_password"
    )

# =========================
# 📚 STUDENTS API
# =========================

# GET - všetci študenti
@app.route('/students', methods=["GET"])
def list_students():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, surname, personality, img FROM students")
    rows = cur.fetchall()

    students = []
    for row in rows:
        students.append({
            "id": row[0],
            "name": row[1],
            "surname": row[2],
            "personality": row[3],
            "img": row[4]
        })

    cur.close()
    conn.close()

    return jsonify(students)

# POST - pridaj študenta
@app.route('/students', methods=["POST"])
def add_student():
    data = request.json

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students (name, surname, personality, img)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        data.get("name"),
        data.get("surname"),
        data.get("personality"),
        data.get("img")
    ))

    new_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Student added", "id": new_id})

# PUT - uprav študenta
@app.route('/students/<int:id>', methods=["PUT"])
def update_student(id):
    data = request.json

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE students
        SET name=%s, surname=%s, personality=%s, img=%s
        WHERE id=%s
    """, (
        data.get("name"),
        data.get("surname"),
        data.get("personality"),
        data.get("img"),
        id
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Student updated"})

# DELETE - zmaž študenta
@app.route('/students/<int:id>', methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE id=%s", (id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Student deleted"})

# =========================
# 💬 CHAT
# =========================

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

# =========================
# 🚀 RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)
