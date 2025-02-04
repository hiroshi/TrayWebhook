import hmac, threading, os, logging, json
from hashlib import sha256
import flask
from flask.ext.sqlalchemy import SQLAlchemy
import requests
#import datastore
from dropbox.client import DropboxClient
from dropbox.datastore import _DatastoreOperations, DatastoreNotFoundError, DatastoreManager

import models

app = flask.Flask(__name__)
app.debug = bool(os.environ.get('DEBUG', False))
app.logger.info("debug=%s", app.debug)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
if app.debug:
    app.config['SQLALCHEMY_ECHO'] = True
# db = SQLAlchemy(app)
models.db.app = app
models.db.init_app(app)

@app.route("/")
def hello():
    return "It may work..."


@app.route("/register", methods=['OPTIONS'])
def register_cors_preflight():
    resp = flask.make_response("OK", 200)
    resp.headers.extend({
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'X-PINGOTHER, Content-Type',
    })
    app.logger.info("preflight")
    return resp


@app.route("/register", methods=['POST'])
def register():
    # FIXME: Make sure this is a valid request by accessing Dropbox API with accessToken
    app.logger.info("data=%s", flask.request.data)
    if flask.request.data:
        val = json.loads(flask.request.data)
        models.Token.insert_unique(uid=val['uid'], kind='AccessToken', token=val['accessToken'])
        models.Token.insert_unique(uid=val['uid'], kind='DeviceToken', token=val['deviceToken'])
        models.db.session.commit()

    resp = flask.make_response("OK", 200)
    if app.debug:
        resp.headers.extend({'Access-Control-Allow-Origin': '*'})
    return resp


@app.route("/webhook", methods=['GET'])
def webhook_challenge():
    return flask.request.args.get('challenge') or "" # verify

@app.route("/webhook", methods=['POST'])
def webhook():
    # Make sure this is a valid request from Dropbox
    if not bool(os.environ.get('SKIP_VERIFY', 0)):
        signature = flask.request.headers.get('X-Dropbox-Signature')
        if signature != hmac.new(os.environ['DROPBOX_APP_SECRET'], flask.request.data, sha256).hexdigest():
            flask.abort(403, "X-Dropbox-Signature not match")
    app.logger.info("data=%s", flask.request.data)
    if flask.request.data:
        val = json.loads(flask.request.data)
        # app.logger.info(data)
        if 'datastore_delta' in val:
            for dsupdate in val['datastore_delta']:
                uid = dsupdate['updater']
                # Get deltas for the datastore
                # datastore.process(uid=uid, handle=change['handle'])
                # Get content from datastore 
                access_token = models.Token.get_token_value(uid=uid, kind='AccessToken')
                if access_token:
                    client = DropboxClient(access_token)
                    dsops = _DatastoreOperations(client)
                    dsinfo = models.DatastoreInfo.query.filter_by(handle=dsupdate['handle']).first()
                    rev = dsinfo.last_process_rev if dsinfo else -1
                    try:
                        resp = dsops.get_deltas(dsupdate['handle'], rev + 1)
                    except DatastoreNotFoundError, e:
                        app.logger.exception(e)
                        app.logger.error("Did you change DROPBOX_APP_SECRET after storing 'AccessToken'?")
                        continue
                    if 'deltas' in resp:
                        deltas = resp['deltas']
                        # Use only last rev for first time
                        if rev == -1:
                            deltas = deltas[-1:]
                        for delta in deltas:
                            for t, tid, rid, data in [x for x in delta['changes'] if x[0] == 'I']:
                                if tid == 'items':
                                    app.logger.info(data['text'])
                                    # Safari PUSH notification
                                    device_token = models.Token.get_token_value(uid=uid, kind='DeviceToken')
                                    if device_token:
                                        app.logger.info("deviceToken: %s", device_token)
                                        payload = {
                                            'auth_token': os.environ['ZEROPUSH_SAFARI_AUTH_TOKEN'],
                                            'device_tokens[]': [device_token],
                                            'title': 'Item added',
                                            'body': data['text']
                                        }
                                        res = requests.post("https://api.zeropush.com/notify", params=payload)
                                        app.logger.info(res)
                                    # iOS PUSH notification
                                    manager = DatastoreManager(client)
                                    datastore = manager.open_default_datastore()
                                    device_token_table = datastore.get_table('deviceTokens')
                                    device_tokens = [r.get_id() for r in device_token_table.query()]
                                    app.logger.info("deviceTokens: %s", device_tokens)
                                    if device_tokens:
                                        payload = {
                                            'auth_token': os.environ['ZEROPUSH_IOS_SERVER_TOKEN'],
                                            'device_tokens[]': device_tokens,
                                            'alert': "Item Added:\n" + data['text'],
                                        }
                                        app.logger.info(payload)
                                        res = requests.post("https://api.zeropush.com/notify", params=payload)
                                        app.logger.info(res)
                            rev = delta['rev']
                    models.DatastoreInfo.upsert(handle=dsupdate['handle'], dsid=dsupdate['dsid'], last_process_rev=rev)
                    models.db.session.commit()

        # We need to respond quickly to the webhook request, so we do the
        # actual work in a separate thread. For more robustness, it's a
        # good idea to add the work to a reliable queue and process the queue
        # in a worker process.
        # threading.Thread(target=process_user, args=(uid,)).start()
    return ""
