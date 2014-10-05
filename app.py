import hmac, threading, os, logging, json
from hashlib import sha256
import flask

app = flask.Flask(__name__)
app.debug = bool(os.environ.get('DEBUG', False))
app.logger.info("debug=%s", app.debug)

@app.route("/")
def hello():
    return "It may works."


@app.route("/register", methods=['POST'])
def register():
    app.logger.info("data=%s", flask.request.data)
    if flask.request.data:
        data = json.loads(flask.request.data)
    resp = flask.make_response("OK", 200)
    if app.debug:
        resp.headers.extend({'Access-Control-Allow-Origin': '*'})
    return resp


@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    # return flask.request.args.get('challenge') or "" # verify
    # Make sure this is a valid request from Dropbox
    if not app.debug:
        signature = flask.request.headers.get('X-Dropbox-Signature')
        if signature != hmac.new(APP_SECRET, flask.request.data, sha256).hexdigest():
            abort(403)
    app.logger.info("data=%s", flask.request.data)
    if flask.request.data:
        data = json.loads(flask.request.data)
        # app.logger.info(data)
    # for uid in data['delta']['users']:
        # We need to respond quickly to the webhook request, so we do the
        # actual work in a separate thread. For more robustness, it's a
        # good idea to add the work to a reliable queue and process the queue
        # in a worker process.
        # threading.Thread(target=process_user, args=(uid,)).start()
    return ""
