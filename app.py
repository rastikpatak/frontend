from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="your_db",
        user="your_user",
        password="your_password"
    )

# ======================
# STUDENTS API
# ======================
@app.route('/str')
def index_page():
    return render_template("index.html")  # musí byť v /templates


@app.route('/students', methods=["GET"])
def get_students():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT id, name, surname, personality, img FROM students")
    rows = cur.fetchall()

    result = [
        {
            "id": r[0],
            "name": r[1],
            "surname": r[2],
            "personality": r[3],
            "img": r[4]
        }
        for r in rows
    ]

    cur.close()
    conn.close()

    return jsonify(result)


@app.route('/students', methods=["POST"])
def add_student():
    data = request.json

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students (name, surname, personality, img)
        VALUES (%s, %s, %s, %s)
    """, (
        data["name"],
        data["surname"],
        data["personality"],
        data["img"]
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Student added"})


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
        data["name"],
        data["surname"],
        data["personality"],
        data["img"],
        id
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "updated"})


@app.route('/students/<int:id>', methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE id=%s", (id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "deleted"})


if __name__ == "__main__":
    app.run(debug=True)
