from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

    @classmethod
    def get_token_value(cls, uid, kind):
        token = cls.query.filter_by(uid=uid, kind=kind).order_by(db.desc(Token.created_at)).first()
        if token:
            return token.token

class DatastoreInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dsid = db.Column(db.String(64))
    handle = db.Column(db.String(64))
    last_process_rev = db.Column(db.Integer)

    def __init__(self, dsid, handle):
        self.dsid = dsid
        self.handle = handle

    @classmethod
    def upsert(cls, dsid, handle, last_process_rev):
        dsinfo = cls.query.filter_by(handle=handle).first()
        if not dsinfo:
            dsinfo = cls(dsid=dsid, handle=handle)
            db.session.add(dsinfo)
        dsinfo.last_process_rev = last_process_rev
