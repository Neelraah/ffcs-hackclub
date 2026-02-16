from flask import Flask, render_template
import requests

app = Flask(__name__)

URL = "https://vitverse.itzdivyanshupatel.workers.dev/faculty-ratings"

@app.route("/")
def index():
    try:
        response = requests.get(URL, timeout=5)
        data = response.json()
        faculty_list = data.get("data", [])
    except Exception as e:
        print("Fetch failed:", e)
        # fallback to local JSON
        import json
        with open("faculty_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            faculty_list = data.get("data", [])

    return render_template("index.html", faculty=faculty_list)

if __name__ == "__main__":
    app.run(debug=True)
