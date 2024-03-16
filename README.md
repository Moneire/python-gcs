# GCSConnector
GCSConnector is a Python library that provides an interface to interact with the [GCS](https://armgs.team/) server. It allows you to login, send messages, refresh sessions, and perform other operations using the GCS server's API.

## Installation
To install the GCSConnector library, you can use pip:

```bash
pip install git+https://github.com/Moneire/python-gcs.git@main 
```
## Usage
Here is a basic usage example:

```python
from gcs.connector import GCSConnector

# Initialize the connector with a username
connector = GCSConnector("sender@exampl.com")

# To get the current logged-in user's info (login and session tokens):
print(connector.get_user())

# To send a message to another user:
connector.send_msg("recipient@exampl.com", "test 1")
# To send a message to user or group chat (by friendly name):
connector.send_msg_by_fname("OIIS Development", "test 2")

# Drop user session
# connector.logout_user()

```

## API
```
set_web_key(key)
```
Sets the web client key.  

<br />

```
GCSConnector(username=None)
```
The constructor for the GCSConnector class. If a username is provided, it will automatically attempt to login the user.

<br />


```
login_user(username)
```
Logs in a user. If the user is already logged-in and the connection is active, it will return the user's data. Otherwise, it will send an OTP to the user's email, and prompt for it in the console. If the OTP is correct, it will log in the user and return their data.

<br />

```
refresh_session()
```
Refreshes the session for the currently logged-in user.

<br />

```
get_user()
```
Returns the data of the currently logged in user.

<br />

```
logout_user()
```
Logs out the currently logged in user.

<br />

```
get_list_of_chats(flush_cache=False)
```
Get list of existing chats for the currently logged-in user. 
After first call it's write chats in the cache.<br /> 
If you want to get actual list from server 
set <b>flush_cache</b> param to <b>True</b>.<br />
Cache automatically flush once a day since class was init.

<br />

```
send_msg(to, message)
```
Sends a message to a specified user.

<br />

```
send_msg_by_fname(fname, message)
```
Sends a message to user or group by friendly name (display name). <br />
Warning: friendly name cached, if you want update data of friendly name list
call ```get_list_of_chats(True)``` first
## Exceptions
The library defines the GCSConnectException exception, which is raised when there is a failure to connect to the GCS server.

## License
[MIT](https://choosealicense.com/licenses/mit/)