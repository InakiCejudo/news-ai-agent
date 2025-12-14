from flask import Flask, request, jsonify
from flask_cors import CORS
from db import create_tables
from models import insert_post, get_posts

app = Flask(__name__)
CORS(app)

create_tables()

@app.route("/api/posts", methods=["POST"])
def add_post():
    data = request.get_json()
    if not data or not 'title' in data or not 'summary' in data:
        return jsonify({"error": "Missing required fields"}), 400

    title = data['title'].strip()
    summary = data['summary'].strip()
    image_url = data.get('image_url', '').strip() or None

    if not title or not summary:
        return jsonify({"error": "Title and summary are required"}), 400

    try:
        post_id = insert_post(title, summary, image_url)
        return jsonify({"success": True, "id": post_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/posts", methods=["GET"])
def fetch_posts():
    try:
        posts = get_posts()
        return jsonify(posts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
