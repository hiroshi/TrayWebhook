import hmac, threading, os, logging, json
from hashlib import sha256
from flask import Flask, request

app = Flask(__name__)
app.debug = bool(os.environ.get('DEBUG', False))
app.logger.info("debug=%s", app.debug)

@app.route("/")
def hello():
    return "Hello World 2"

@app.route("/webhook", methods=['GET', 'POST'])
def webhook():
    # return request.args.get('challenge') or "" # verify
    # Make sure this is a valid request from Dropbox
    if not app.debug:
        signature = request.headers.get('X-Dropbox-Signature')
        if signature != hmac.new(APP_SECRET, request.data, sha256).hexdigest():
            abort(403)
    app.logger.info("data=%s", request.data)
    if request.data:
        data = json.loads(request.data)
        app.logger.info(data)
    # for uid in data['delta']['users']:
        # We need to respond quickly to the webhook request, so we do the
        # actual work in a separate thread. For more robustness, it's a
        # good idea to add the work to a reliable queue and process the queue
        # in a worker process.
        # threading.Thread(target=process_user, args=(uid,)).start()
    return ''
