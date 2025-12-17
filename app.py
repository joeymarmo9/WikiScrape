from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # <-- ADDED: allows requests from SiteGround frontend

from scraper import scrape
from nlp_analysis import analyze_tree

app = Flask(__name__)
CORS(app)  # <-- ADDED: enable Cross-Origin Resource Sharing

MAX_NODES_CAP = 200
MAX_DEPTH_CAP = 6


@app.get("/")
def index():
    return jsonify({"ok": True, "message": "WikiScrape API running"}), 200


@app.post("/api/run")
def api_run():
    data = request.get_json(force=True, silent=True) or {}

    url = (data.get("url") or "").strip()
    num_nodes = int(data.get("num_nodes") or 30)
    max_depth = int(data.get("max_depth") or 2)
    run_nlp = bool(data.get("run_nlp", True))

    if not url:
        return jsonify({"error": "Missing 'url'"}), 400

    num_nodes = max(1, min(num_nodes, MAX_NODES_CAP))
    max_depth = max(0, min(max_depth, MAX_DEPTH_CAP))

    try:
        tree = scrape(url=url, num_nodes=num_nodes, max_depth=max_depth)

        payload = {
            "scrape": tree
        }

        if run_nlp:
            payload["nlp"] = analyze_tree(tree)

        return jsonify(payload)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
