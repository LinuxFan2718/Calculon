# Calculon
cryptocurrency trading bot using the Coinbase Pro API

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
