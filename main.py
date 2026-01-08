from flask import Flask, request, jsonify

app = Flask(__name__)

def check_number(number):
    if number > 0:
        return f"{number} is POSITIVE"
    elif number < 0:
        return f"{number} is NEGATIVE"
    else:
        return f"{number} is ZERO"

@app.route("/", methods=["GET"])
def home():
    return "Use /check?number=VALUE"

@app.route("/check", methods=["GET"])
def check():
    number_str = request.args.get("number")
    if number_str is None:
        return jsonify({"error": "number parameter is required"}), 400
    try:
        number = float(number_str)
        result = check_number(number)
        return jsonify({"result": result})
    except ValueError:
        return jsonify({"error": "invalid number"}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)