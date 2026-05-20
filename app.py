import os
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import psycopg2

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT")
    )

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/students", methods=["GET"])
def get_students():
    sort = request.args.get("sort", "id")
    order = request.args.get("order", "asc")

    sort_map = {
        "id": "id",
        "name": "name",
        "surname": "surname"
    }

    if sort not in sort_map:
        sort = "id"

    if order not in ["asc", "desc"]:
        order = "asc"

    conn = get_db_connection()
    cur = conn.cursor()

    query = f"""
        SELECT id, name, surname, img
        FROM students
        ORDER BY {sort_map[sort]} {order.upper()}
    """

    cur.execute(query)
    rows = cur.fetchall()

    students = []
    for r in rows:
        students.append({
            "id": r[0],
            "name": r[1],
            "surname": r[2],
            "img": r[3]
        })

    cur.close()
    conn.close()

    return jsonify(students)

@app.route("/students", methods=["POST"])
def add_student():
    data = request.json

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO students (name, surname, img)
        VALUES (%s, %s, %s)
    """, (
        data.get("name"),
        data.get("surname"),
        data.get("img", "")
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"ok": True})

@app.route("/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM students WHERE id=%s", (id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"deleted": True})

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
