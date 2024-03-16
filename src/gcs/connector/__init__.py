import sys
import getpass
import uuid
from datetime import datetime

import keyring
import requests


class GCSConnectException(Exception):
    pass


class GCSConnector:

    def __init__(self, username=None):

        # Web client key
        self.__k = "dGFybS13ZWIK"

        # API domain
        self.__domain = "u.armgs.team"
        self.__base_url = "https://" + self.__domain + "/api/v120/"

        # Define the headers for methods in a dictionary
        self.__headers = {
            "authority": self.__domain,
            "accept": "/",
            # "accept-language": "en-US,en;q=0.9",
            "content-type": "application/x-www-form-urlencoded",
            # "origin": "https://webim.armgs.team",
            # "referer": "https://webim.armgs.team/",
            # "sec-ch-ua": '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            # "sec-ch-ua-mobile": "?0",
            # "sec-ch-ua-platform": '"macOS"',
            # "sec-fetch-dest": "empty",
            # "sec-fetch-mode": "cors",
            # "sec-fetch-site": "same-site",
            "user-agent": "Chrome/122.0.0.0"
            # "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }

        # Define the GET parameters for login methods in a dictionary
        self.__login_params = {
            "tokenType": "otp_via_email",
            "clientName": "webVKTeams",
            "clientVersion": "VKTeams Web  " + self.__k,  # + " 23.12.11(2024/03/06 17:45 release/23.12i) mac desktop",
            "idType": "ICQ",
            "s": "username@example.com",
            "k": self.__k
        }

        # Define the data to be sent in login methods
        self.__login_data = {
            "pwd": "1"
        }

        # User obj
        self.__user = None
        # User list of chat
        self.__user_chats = None

        if username is not None:
            self.login_user(username)

    def set_web_key(self, key):
        self.__k = key

    def login_user(self, username):
        self.__login_params["s"] = username

        a = keyring.get_password("python-gcs", username + ":a")
        aimsid = keyring.get_password("python-gcs", username + ":aimsid")
        self.__user = {
            "login": username,
            "a": a,
            "aimsid": aimsid
        }

        if bool(a) and bool(aimsid):
            if self.get_list_of_chats(True):
                return self.__user
            else:
                if self.refresh_session() and self.get_list_of_chats(True):
                    return self.__user

        if self.__send_otp_via_email():

            if not sys.stdin.isatty():
                otp_pass = input('Code from email: ')
            else:
                otp_pass = getpass.getpass('Code from email: ')

            userdata = self.__get_user_token(otp_pass)
            if bool(userdata):
                self.__user = {
                    "login": username,
                    "a": userdata["token"]["a"],
                    "aimsid": ""
                }
                self.__start_sessions()
                if bool(self.__user):
                    keyring.set_password("python-gcs", username + ":a", self.__user["a"])
                    keyring.set_password("python-gcs", username + ":aimsid", self.__user["aimsid"])

                    self.get_list_of_chats(True)
                    return self.__user

        raise GCSConnectException("Fail to connect to GCS server")

    def refresh_session(self):

        self.__start_sessions()
        if bool(self.__user):
            keyring.set_password("python-gcs", self.__user["login"] + ":a", self.__user["a"])
            keyring.set_password("python-gcs", self.__user["login"] + ":aimsid", self.__user["aimsid"])

            return self.__user

        return False

    def get_user(self):
        return self.__user

    def logout_user(self):
        keyring.delete_password("python-gcs", self.__user["login"] + ":a")
        keyring.delete_password("python-gcs", self.__user["login"] + ":aimsid")

    def send_msg(self, to, message):
        data = {
            't': to,
            'r': '7386-' + str(datetime.now().second),
            'mentions': '',
            'message': message,
            'f': 'json',
            'aimsid': self.__user["aimsid"]
        }
        res = requests.post(self.__base_url + "wim/im/sendIM", headers=self.__headers, data=data)
        if res.ok and res.json()["response"]["statusCode"] == 200:
            return True
        else:
            print("Error: " + res.text, file=sys.stderr)
            return False

    def send_msg_by_fname(self, fname, message):

        aim_id = next(
            (obj["aimId"] for obj in self.get_list_of_chats() if 'friendly' in obj and obj["friendly"] == fname), None)

        if self.send_msg(aim_id, message):
            return True
        else:
            return False

    def get_list_of_chats(self, flush_cache=False):

        if (not flush_cache and self.__user_chats is not None
                and datetime.now().second - self.__user_chats["timestamp"] < 60 * 60 * 24):
            return self.__user_chats["data"]

        # GET parameters
        params = {
            "aimsid": self.__user["aimsid"],
            "first": "1",
            "rnd": str(datetime.now().second) + ".977186",
            "timeout": "500"
        }

        # Send the request
        res = requests.get(self.__base_url + "/bos/a10-1/aim/fetchEvents", headers=self.__headers, params=params)

        if res.ok and res.json()["response"]["statusCode"] == 200:
            group_list = next((obj["eventData"]["groups"] for obj in res.json()["response"]["data"]["events"]
                               if obj["type"] == "buddylist"), None)
            buddy_list = [buddy for group in group_list for buddy in group["buddies"]]

            self.__user_chats = {"timestamp": datetime.now().second, "data": buddy_list}
            return buddy_list
        else:
            print("Error: " + res.text, file=sys.stderr)
            return False

    def __get_unic_address(self):
        mac_num = hex(uuid.getnode()).replace('0x', '').upper()
        mac = '-'.join(mac_num[i: i + 2] for i in range(0, 11, 2))
        return mac.join("-").join(str(datetime.now().second))

    def __send_otp_via_email(self):
        # set settings for sending otp
        self.__login_params["tokenType"] = "otp_via_email"
        self.__login_data["pwd"] = "1"

        res = requests.post(self.__base_url + "wim/auth/clientLogin",
                            params=self.__login_params, headers=self.__headers, data=self.__login_data)
        if res.ok and res.json()["response"]["statusCode"] == 200:
            return True
        else:
            print("Error: " + res.text, file=sys.stderr)
            return False

    def __get_user_token(self, otp_pass):
        # set settings for login
        self.__login_params["tokenType"] = "longTerm"
        self.__login_data["pwd"] = otp_pass

        res = requests.post(self.__base_url + "wim/auth/clientLogin",
                            params=self.__login_params, headers=self.__headers, data=self.__login_data)
        if res.ok and res.json()["response"]["statusCode"] == 200:
            return res.json()["response"]["data"]
        else:
            print("Error: " + res.text, file=sys.stderr)
            return False

    def __start_sessions(self):
        params = {
            'ts': str(datetime.now().second),
            'a': self.__user["a"],
            'userSn': self.__user["login"],
            'k': self.__k,
            'view': 'online',
            'clientName': 'webVKTeams',
            'language': 'en-US',
            'deviceId': self.__get_unic_address(),  # '292a5e-0057-7396-da97-668fe29fe5b7',
            'sessionTimeout': '2592000',
            'subscriptions': 'status',
            'events': 'myInfo,presence,buddylist,typing,hiddenChat,hist,mchat,sentIM,imState,dataIM,offlineIM,userAddedToBuddyList,service,lifestream,apps,permitDeny,diff,webrtcMsg',
            'includePresenceFields': 'aimId,displayId,friendly,friendlyName,state,userType,statusMsg,statusTime,lastseen,ssl,mute,counterEnabled,abContactName,abPhoneNumber,abPhones,official,quiet,autoAddition,largeIconId,nick,userState'
        }

        res = requests.post(self.__base_url + "wim/aim/startSession", headers=self.__headers, params=params)
        if res.ok and res.json()["response"]["statusCode"] == 200:
            self.__user["aimsid"] = res.json()["response"]["data"]["aimsid"]
            return self.__user
        else:
            print("Error: " + res.text, file=sys.stderr)
            return False

    def __check_connection(self):
        params = {
            'suggest': '1',
            'aimsid': self.__user["aimsid"],
            'lang': 'en_US',
            'client': 'VKTeams',
            'platform': 'web',
            'a': self.__user["a"],
            'k': self.__k,
            'ts': str(datetime.now().second)
        }
        res = requests.post(self.__base_url + "store/store/my", headers=self.__headers, params=params)
        if res.ok:
            return True
        else:
            print("Error: " + res.text, file=sys.stderr)
            return False
