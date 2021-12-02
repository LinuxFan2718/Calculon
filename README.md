# Calculon
cryptocurrency trading bot using the Coinbase Pro API

# Requirements

To run this software you need experience using python and cron, and
a server to run the software 24/7.

I am building a web app to make it easy for anyone to use it,
coming soon!

# Library

[cbpro](https://github.com/danpaquin/coinbasepro-python)

# How to use

## Check out this repo

```bash
git clone git@github.com:LinuxFan2718/Calculon.git
cd Calculon
```

## Install python libraries

```bash
pip install -r requirements.txt
```

## Connect your Coinbase Pro account to the bot

```bash
cp .env.example .env
```

Open `.env` in a text editor.

Go to the [Coinbase Pro API page](https://pro.coinbase.com/profile/api)
and generate a key with view, transfer and trade permissions.

Copy the api key, passphrase and api secret into `.env`.

Do not share these values with anyone or check them into a git repo.

To test your Coinbase Pro API config, run test-auth.py, the output will
tell you whether your `.env` values are working.

```bash
python test-auth.py
```

## Buy crypto with USD

You must have a funding method configured in Coinbase Pro

Configure the constants at the top of the file `dca.py` for
the amount and cryptocurrency you want.

Then run the file to buy.

```bash
python dca.py
```

I recommended setting up this file to run using cron every week
or month to take advantage of
[dollar cost averaging](https://www.investopedia.com/terms/d/dollarcostaveraging.asp).

## Using cron to autobuy

First, ssh into your server.

As your user, pull down the git repo, and create the `.env`
file on your server in the repo.

I had to specify the full path when loading the env file, so
edit the source code like this. (My user on this server is
named ethereum, this used to be a ethereum node server.)

```diff
-config = dotenv_values(".env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}
+config = dotenv_values("/home/ethereum/Calculon/.env")  # config = {"USER": "foo", "EMAIL": "foo@example.org"}
```

You'll need to create a shell script that runs the python
script. Mine looks like this, named dailybuy.sh

```bash
#!/bin/bash

/home/ethereum/.pyenv/shims/python /home/ethereum/Calculon/dca.py
```

As you can see, I installed pyenv on my server. However you install
python, make a shell script using full paths for python and the source
code file.

For this part, I recommend making the above changes to test-auth.py
and created a dailytest.sh script to run it, so you can test your cron
setup.

To edit cron, don't try to edit /etc/crontab as root. Instead, as your
regular user, run `crontab -e`. Add a line like this

```
* * * * * /home/ethereum/Calculon/dailytest.sh >> /home/ethereum/cron.log 2>&1
```

No need to send SIGHUP to the cron service. Just save your changes,
then run

```bash
tail -f ~/cron.log
```

Fix any errors you see, this setup will test your credentials every single
minute of every day, so once it works, comment out that line.

Now add a line to crontab running your daily buy, set the time to once a day,
and watch it happen by tail -f your cron log file, and in the Coinbase Pro
interface!

For example,

```
50 5 * * * /home/ethereum/Calculon/dailybuy.sh >> /home/ethereum/cron.log 2>&1
```

Does a daily buy at 5:50am UTC. Check your cron timezone with

```bash
cat /etc/localtime
```

Also useful is

```bash
date
```

## Question: How do you save money buying ETH with Calculon?

Answer: For some reason, Coinbase charges a much higher fee when
you buy using www.coinbase.com vs. using Coinbase Pro. You can
get the lower price using pro.coinbase.com, or using their API
with a bot like this one.

## Fee advantage

On Sat, May 29 at 5:25pm ET I executed a $100 ETH buy using this
dca script. 

### Coinbase Pro buy

0.04435264 ETH

### Coinbase UI buy

0.0430622 ETH

### Difference

0.00129044 ETH which is $2.89

## How to set up roberto

Create a separate "Portfolio" in the Coinbase Pro web console and fund it with USD and the desired token to trade.

Create an API key in the new Portfolio without transfer permission.

Add the API key to `.env` in this directory, in the keys starting with BEGINNER. (See the roberto.py source code if a hint is needed.)

Edit the constants at the top of roberto.py

Run `roberto.py` to set up limit orders for 10 dollars worth of ETH with a 5 percent separation (buy low, sell high)

```python
python roberto.py ETH-USD 10.0 5.0
```

You should see some info printed to the terminal.

## How to set up cron_roberto

On Mac, I used `crontab -e` to set up a cron job which looks like

```
* * * * * cd ~/Git/Calculon/ && /anaconda3/envs/calculon/bin/python cron_roberto.py ETH-USD 1000.0 5.0
```

The first command just changes the directory to where the API key is,
the second calls `cron_roberto.py` which will check if any orders have executed, 
and if they have, set up a new pair using roberto.set_limit_orders().

You can also run directly from the command line like

```
python cron_roberto.py ETH-USD 10.0 5.0
```
