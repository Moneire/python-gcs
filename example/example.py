from gcs.connector import GCSConnector

# Initialize the connector with a username
connector = GCSConnector("sender@exampl.com")

# To get the current logged-in user's info (login and session tokens):
print(connector.get_user())

# To send a message to another user:
connector.send_msg("recipient@exampl.com", "test 1")
# To send a message to user or group chat (by friendly name):
connector.send_msg_by_fname("OIIS Development", "test 2")