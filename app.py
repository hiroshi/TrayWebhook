from flask import Flask, request

app = Flask(__name__)
app.debug = True

@app.route("/")
def hello():
    return "Hello World 2"

@app.route("/webhook", methods=['GET'])
def webhook():
    return request.args.get('challenge') or ""
