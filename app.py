import json

from flask import Flask, jsonify, request
from pymongo import MongoClient



app = Flask(__name__)
client = MongoClient("mongodb://localhost:27017/")
database = client["new_note"]



@app.route("/register", methods=["post"])
def create_register():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    if database.users.find_one({"email": email}):
        return jsonify({"message": "user already exists"}), 400

    else:
        user = ({"name": name, "email": email, "password": password})
        database.users.insert_one(user)
        return jsonify({"message": "Successfully register"}), 201



@app.route("/login",methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    user = database.users.find_one({"email": email})
    if user and user["password"] == password:
      return jsonify({"message": "your have successfully login"}), 200
    else:
        return jsonify({"message": "invalid credential"}), 400



@app.route("/notes", methods=["POST"])
def add_note():
        # database.notes.create_index('title', unique=True)
        data = request.get_json()
        content = data.get("content")
        title = data.get("title")

        if database.notes.find_one({"title": title}):
            return jsonify({'message': 'Note already exists'}), 400
        else:
            database.notes.insert_one({"content": content, "title": title})
            return jsonify({"message": "Note created"}), 201


@app.route("/notes/<string:title>", methods=["GET"])
def get_note(title):
    try:
        note = database.notes.find_one({"title": title})
        if note:
            return jsonify({"title": note["title"], "content": note["content"]})
        else:
            return jsonify({"message": "Note not found"}), 404
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@app.route("/delete/<string:title>", methods=["DELETE"])
def delete_note(title):
    try:
        note = database.notes.find_one({"title": title})
        if not note:
            return jsonify({"message": "Note not found"}), 404
        else:
            database.notes.delete_one({"title": title})
            return jsonify({"message": "Note deleted"}), 200
    except Exception as e:
        return jsonify({"message": "An error occurred", "error": str(e)}), 500


@app.route("/update/<string:title>", methods=["PATCH"])
def update_note(title):
    note = database.notes.find_one({"title": title})
    if not note:
        return jsonify({"message": "Note not found"}), 404
    else:
        data = request.get_json()
        content = data.get("content")
        title = data.get("title")
        database.notes.update_one(
            {"title": title},
            {"$set": {"content": content, "title": title}}
        )
        return jsonify({"message": "note successfully updated "}), 201


@app.route("/notes", methods=["GET"])
def get_all_notes():
    note = database.notes.find()
    store_note = []
    for notes in note:
        store_note.append({"content": notes["title"], "title": notes["title"]})
        return jsonify(store_note)


if __name__ == "__main__":
    app.run(debug=True)
