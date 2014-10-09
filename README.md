TrayPythonWebhook
=================

Local development
-----------------

    $ virutalenv venv
    $ . venv/bin/activate


When you leave virtualenv:

    $ deactivate

### Create local PostgreSQL database

    $ createdb tray

### Create .env

    DATABASE_URL=postgres://localhost:5432/tray

If you want some debug logging.

    DEBUG=1

- Don't contains spaces around '=' (For env command compatibility.)


### Initialize database

    $ env `cat .env` python
    >>> from app import db
    >>> db.create_all()


### Start development server

    $ foreman start web


### Test /webhook

    $ curl -v -H "Content-Type: application/json" -d '{"datastore_delta":[{"owner":348426, "dsid":"default"}]}' http://localhost:5000/webhook


### Adding another python package

    $ pip install a_package
    $ pip freeze > requirements.txt
