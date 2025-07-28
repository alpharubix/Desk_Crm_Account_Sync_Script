import requests
import dotenv
import os
dotenv.load_dotenv(override=True)

class AccessToken:
    def __init__(self):
        self.crm_access_token = None
        self.desk_access_token = None

    def generate_token_for_desk(self):
        body = {
            "client_id": os.getenv("DESK_CLIENT_ID"),
            "client_secret": os.getenv("DESK_SECRET_KEY"),
            "refresh_token": os.getenv("DESK_REFRESHMENT_TOKEN"),
            "grant_type": "refresh_token",
        }
        try:
            response = requests.post("https://accounts.zoho.com/oauth/v2/token", data=body)
            data = response.json()
            print(response.status_code)
            print(response.text)
            access_token = data["access_token"]
            self.desk_access_token = access_token
            print(self.desk_access_token)
            return self
        except Exception as e:
            print(e)

    def generate_access_token_for_crm(self):

        body = {
            "client_id": os.getenv("CRM_CLIENT_ID"),
            "client_secret": os.getenv("CRM_SECRET_KEY"),
            "refresh_token": os.getenv("CRM_REFRESHMENT_TOKEN"),
            "grant_type": "refresh_token",
        }
        try:
            response = requests.post("https://accounts.zoho.com/oauth/v2/token", data=body)
            data = response.json()
            access_token = data["access_token"]
            self.crm_access_token = access_token
            print(self.crm_access_token)
            return self
        except Exception as e:
            print(e)