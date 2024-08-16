from flask import Flask, request, jsonify
import parser

app = Flask(__name__)

@app.route("/api", methods=["GET"])
def response():
    return {"Channel":"The Show", "tutorial":"Flask React"}

@app.route("/test", methods=["GET"])
def test():
    return {"Channel":"TEST SUCCESS", "tutorial":"IDK ANYMORE"}

@app.route("/parse", methods=["GET"])
def parse():
    prompt = request.args.get('prompt')
    print("changes")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    parser.parse(prompt)
    return {"Channel":"Parse", "tutorial":"IDK ANYMORE"}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')