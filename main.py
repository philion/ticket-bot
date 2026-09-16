import os
import json

from python_freeipa import ClientMeta
from dotenv import load_dotenv


def init_client() -> ClientMeta:
    load_dotenv()  # load environment variables

    host = os.getenv("FREEIPA_HOST")
    username = os.getenv("FREEIPA_USER")
    token = os.getenv("FREEIPA_TOKEN")
    # TODO Validate env

    client = ClientMeta(host, verify_ssl=False) # FIXME with real certs
    client.login(username, token)

    return client


def main():

    client = init_client()

    client.user_mod("philion", o_addattr="attrName=attrValue")

    user = client.user_show("philion")
    print(json.dumps(user, indent=4))





if __name__ == "__main__":
    main()
