from flask import Flask, jsonify, render_template
@app.route('/')
def pusti_stranku():
    return render_template("index.html")
