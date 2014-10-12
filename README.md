TrayPythonWebhook
=================



Local development setup
-----------------------

    $ virutalenv venv
    $ . venv/bin/activate
    $ pip install -r requirements.txt

When you leave virtualenv:

    $ deactivate

### Create local PostgreSQL database

    $ createdb tray

### Create .env

    DATABASE_URL=postgres://localhost:5432/tray
    ZEROPUSH_AUTH_TOKEN=<Your Zeropush Auth Token>
    SKIP_VERIFY=1

- Don't contains spaces around '=' (For env command compatibility.)


### Initialize database

    $ env `cat .env` python
    >>> from app import models
    >>> models.db.create_all()


### Start development server

    $ foreman start web


### Test /webhook

Example:

    $ curl -v -H "Content-Type: application/json" -d '{"datastore_delta": [{"updater": 348426, "dsid": "default", "handle": "R5uT1VDSI8lz3LoQYjv30IgJ9fyEDW", "change_type": "update", "owner": 348426}]}' http://localhost:5000/webhook

You may see exact data in `heroku logs -t`.

### Adding another python package

    $ pip install a_package
    $ pip freeze > requirements.txt


Heroku setup
------------

    $ heroku create <Your App Name>
    $ git push heroku master
    $ heroku addons:add heroku-postgresq
    $ heroku config:set ZEROPUSH_AUTH_TOKEN=<Your Token Here> DROPBOX_APP_SECRET=<Your Dropbox App Secret>
    $ heroku run python
    >>> from app import models
    >>> models.db.create_all()


How it works
------------

- Open web app with Safari (Mavericks or later) and login via Dropbox.
-- It will POST /register so that Dropbox access token and Safari device token are stored.
- Add item from the iOS App.
-- /webhook is called then send PUSH notification to the Safari.
