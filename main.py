import os
import json
import random
import string
from python_freeipa import ClientMeta
from python_freeipa.exceptions import DuplicateEntry
from dotenv import load_dotenv
import gitlab


def init_client() -> ClientMeta:
    load_dotenv()  # load environment variables

    host = os.getenv("FREEIPA_HOST")
    username = os.getenv("FREEIPA_USER")
    token = os.getenv("FREEIPA_TOKEN")
    # TODO Validate env

    client = ClientMeta(host, verify_ssl=False) # FIXME with real certs
    client.login(username, token)

    return client


class GitlabWrapper:
    def __init__(self):
        load_dotenv()  # load environment variables

        url = os.getenv("GITLAB_URL")
        token = os.getenv("GITLAB_TOKEN")

        self.client = gitlab.Gitlab(url=url, private_token=token)


    def get_user(self, username:str):
        return self.client.users.list(username=username, get_all=False)[0]


    def get_all_users(self):
        return self.client.users.list(get_all=True)


LDAP_groups = ['scnusers'] # FIXME: Move to env: APPROVED_USER_GROUPS - list of group names to add the user to


class UserManager:
    def __init__(self):
        self.ldap = init_client()

    def lookup_discord_id(self, discord_id:str):
        response = self.ldap.user_find(o_gecos=discord_id)
        print(response)
        if not response or response['count'] == 0:
            # try staged users
            response = self.ldap.stageuser_find(o_gecos=discord_id)
        return response['result']


    def create_stage_user(self, username:str, first:str, last:str, email:str, discord_id:str):
        try:
            response = self.ldap.stageuser_add(
                a_uid=username,
                o_givenname=first,
                o_sn=last,
                o_cn=" ".join([first, last]),
                o_mail=email,
                o_gecos=discord_id,
                o_random=True)

            # print("----------")
            # print(json.dumps(response, indent=4))
            # print("----------")

            user_record = response['result']
            passwd = user_record['randompassword']
            print("!!! new user passwd:", passwd)

            return user_record

        except DuplicateEntry as e:
            print(e)
            return None


    def approve_stage_user(self, user:str):
        try:
            response = self.ldap.stageuser_activate(user)
            # validate response

            # add approved user to required groups
            for group_name in LDAP_groups:
                result = self.ldap.group_add_member(group_name, o_user=user)
                print('### add group:', group_name, result)

            # create a new gitlab user

            return response['result']
        except DuplicateEntry as e:
            print(e)
            return None


    def get_stage_users(self, sizelimit:int=0):
        response = self.ldap.stageuser_find()
        # valid response
        return response['result']


    def delete_stage_user(self, user:str):
        response = self.ldap.stageuser_del(user)
        print(response['summary'])


def main():
    # gl = GitlabWrapper()

    # user = gl.get_user("philion")
    # print(user)

    # for user in gl.get_all_users():
    #     print(user)

    username = "a-test-user"
    discord_id = ''.join(random.choices(string.digits, k=8))
    #passwd = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    #print("discord id:", discord_id)

    users = UserManager()
    user = users.create_stage_user(username, "Annie", "Test", "test@example.com", discord_id)
    print("state user:", user)

    result = users.approve_stage_user(username)
    print("approval:", result)

    #user = users.lookup_discord_id(discord_id)
    #stage_users = users.get_stage_users()
    #for user in stage_users:
    #    print(json.dumps(user, indent=4))
    #print(type(user[0]))
    #print(user)

    #users.delete_stage_user(username)


    #client = init_client()

    #client.user_mod("philion", o_gecos="DiscordID")
    #user = client.user_find(o_gecos="DiscordID")
    #user = client.user_show("philion")

    #client.stageuser_add(a_uid="another-test", o_givenname="Another", o_sn="Test", o_cn="Another Test", o_gecos="54342")

    #client.stageuser_activate("another-test")
    #client.group_add_member("scnusers", o_user="another-test")





if __name__ == "__main__":
    main()
