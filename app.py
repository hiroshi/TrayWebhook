import hmac, threading, os, logging, json
from hashlib import sha256
import flask
from flask.ext.sqlalchemy import SQLAlchemy

app = flask.Flask(__name__)
app.debug = bool(os.environ.get('DEBUG', False))
app.logger.info("debug=%s", app.debug)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
if app.debug:
    app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer)
    kind = db.Column(db.String(20))
    token = db.Column(db.String(80), unique=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

    def __init__(self, uid, kind, token):
        self.uid = uid
        self.kind = kind
        self.token = token

    def __repr__(self):
        return '<Token uid=%r kind=%r token=%r>' % (self.uid, self.kind, self.token)

    @classmethod
    def insert_unique(cls, **kwargs):
        if not cls.query.filter_by(**kwargs).first():
            db.session.add(cls(**kwargs))


@app.route("/")
def hello():
    return "It may works."


@app.route("/register", methods=['OPTIONS'])
def preflight():
    resp = flask.make_response("OK", 200)
    if app.debug:
        resp.headers.extend({
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'X-PINGOTHER, Content-Type',
        })
    app.logger.info("preflight")
    return resp


@app.route("/register", methods=['POST'])
def register():
    app.logger.info("data=%s", flask.request.data)
    if flask.request.data:
        val = json.loads(flask.request.data)
        Token.insert_unique(uid=val['uid'], kind='AccessToken', token=val['accessToken'])
        Token.insert_unique(uid=val['uid'], kind='DeviceToken', token=val['deviceToken'])
        db.session.commit()

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
        val = json.loads(flask.request.data)
        # app.logger.info(data)
    # for uid in data['delta']['users']:
        # We need to respond quickly to the webhook request, so we do the
        # actual work in a separate thread. For more robustness, it's a
        # good idea to add the work to a reliable queue and process the queue
        # in a worker process.
        # threading.Thread(target=process_user, args=(uid,)).start()
    return ""
