from flask import Flask, request, jsonify
from modules.static_analysis.analyzer import analyze_code

app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return "Welcome to the backend."


@app.route('/submit-code', methods=['POST'])
def submit_code():
    data = request.get_json()
    code_snippet = data.get('code')
    if not code_snippet:
        return jsonify({"error": "No code provided"}), 400
    # TODO for vulnerability analysis

    # TODO integrate the static analysis tool,
    result = analyze_code(code_snippet)

    # TODO LLM-based analysis

    # TODO RAG module.

    return jsonify(result), 200


if __name__ == '__main__':
    app.run(debug=True)
