from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return "Welcome to the backend."


@app.route('/submit-code', methods=['POST'])
def submit_code():
    data = request.get_json()
    code_snippet = data.get('code')

    # TODO for vulnerability analysis:
    # TODO integrate the static analysis tool,
    # TODO LLM-based analysis
    # TODO RAG module.
    result = {
        "vulnerabilities": [],
        "message": "Code received successfully. Analysis pending.",
        "code": code_snippet
    }

    return jsonify(result), 200


if __name__ == '__main__':
    app.run(debug=True)
