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
async def parse():
    prompt = request.args.get('prompt')
    print("idk")
    if not prompt:
        return jsonify({"error": "No prompt provided"}), 400
    candidates = await parser.parse(prompt)
    return {"candidates":candidates}

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')