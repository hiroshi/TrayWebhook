import os
from dropbox.client import DropboxClient, DropboxOAuth2Flow, DropboxOAuth2FlowNoRedirect
from dropbox.rest import ErrorResponse, RESTSocketError
from dropbox.datastore import DatastoreError, DatastoreManager, Datastore, Date, Bytes

access_token = os.environ['DROPBOX_ACCESS_TOKEN']
client = DropboxClient(access_token)
manager = DatastoreManager(client)

shared_dsid = os.environ['DROPBOX_SHARED_QUEUE_DSID']
if shared_dsid:
    datastore = manager.open_datastore(shared_dsid)
else:
    datastore = manager.create_datastore()
    datastore.set_role(Datastore.PUBLIC, Datastore.EDITOR)
    datastore.commit()
    print("Shared datastore created (id: %s)." % datastore.get_id())
