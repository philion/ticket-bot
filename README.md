Sample code for testing LDAP.

Clone project and initialize submodules:
```
git clone https://github.com/philion/ticket-bot
cd ticket-bot
git submodule update --init --recursive
```

Create `.env` file with:
```
FREEIPA_HOST=<ldap-host>
FREEIPA_USER=<user-name>
FREEIPA_TOKEN=<user-token>
```

Then:

`uv run main.py`


To run redmine with the kanban plugin:

`docker compose up -d`