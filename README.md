TrayPythonWebhook
=================



Local development
-----------------

If you didn't do "Local development setup", do it.

### Enter virtualenv

    $ source venv/bin/activate


### Start development server

    $ foreman start web


### Test /webhook

Before calling the webhook, you need to regiter device tokens.
- For Safari PUSH notifications, see [Tray web app](https://github.com/hiroshi/tray)
- For iOS PUSH notifications, see [Tray iOS app](https://github.com/hiroshi/TrayiOS)

Example:

    $ curl -v -H "Content-Type: application/json" -d '{"datastore_delta": [{"updater": 348426, "dsid": "default", "handle": "R5uT1VDSI8lz3LoQYjv30IgJ9fyEDW", "change_type": "update", "owner": 348426}]}' http://localhost:5000/webhook





Local development setup
-----------------------

### Create local PostgreSQL database

Install PostgreSQL from http://postgresapp.com.
Set PATH in your .bashrc, .zshrc or whatever you use.

    PATH=/Applications/Postgres.app/Contents/Versions/9.3/bin:$PATH

It is needed before `pip install -r requirements.txt` becase `psycopg2` require `pg_config`.

    $ createdb tray


## python environment

    $ virutalenv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt


### Create .env

    DATABASE_URL=postgres://localhost:5432/tray
    ZEROPUSH_AUTH_TOKEN=<Your Zeropush Auth Token>
    SKIP_VERIFY=1
    DEBUG=1


### Initialize database

    $ dotenv python
    >>> from app import models
    >>> models.db.create_all()


Heroku setup
------------

    $ heroku create <Your App Name>
    $ git push heroku master
    $ heroku addons:add heroku-postgresq
    $ heroku config:set ZEROPUSH_AUTH_TOKEN=<Your Token Here> DROPBOX_APP_SECRET=<Your Dropbox App Secret>
    $ heroku run python
    >>> from app import models
    >>> models.db.create_all()


Misc
----

### Adding another python package

    (venv)$ pip install a_package
    (venv)$ pip freeze > requirements.txt


How it works
------------

- Open web app with Safari (Mavericks or later) and login via Dropbox.
  - It will POST /register so that Dropbox access token and Safari device token are stored.
- Add item from the iOS App.
  - /webhook is called then send PUSH notification to the Safari.
