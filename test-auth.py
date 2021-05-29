import cbpro
from dotenv import dotenv_values

config = dotenv_values(".env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}
key = config['API_KEY']
b64secret = config['API_SECRET']
passphrase = config['PASSPHRASE']

auth_client = cbpro.AuthenticatedClient(key, b64secret, passphrase)
pass
accounts = auth_client.get_accounts()
if type(accounts) is dict:
  print("invalid config")
  print(accounts)
elif type(accounts) is list:
  print("valid config")
  print(accounts[0]['currency'])