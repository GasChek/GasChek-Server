import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

PAYSTACK_SECRET_KEY = os.getenv('PAYSTACK_SECRET_KEY')


def initialize_payment(email, price, fee, subaccount_code, callback_url, cylinder, gas_dealer):
    url = 'https://api.paystack.co/transaction/initialize'
    headers = {
        'Authorization': PAYSTACK_SECRET_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    dataa = {
        "email": email,
        "amount": (price + fee) * 100,
        "subaccount": subaccount_code,
        "bearer": "account",
        "callback_url": callback_url,
        "metadata": {
            "custom_fields": [
                {
                    "display_name": "Gas Dealer",
                    "variable_name": "Gas Dealer",
                    "value": gas_dealer
                },
                {
                    "display_name": "Cylinder",
                    "variable_name": "Cylinder",
                    "value": "{} kg".format(cylinder)
                },
                {
                    "display_name": "Price",
                    "variable_name": "Price",
                    "value": "NGN {}".format(price)
                },
                {
                    "display_name": "Delivery fee",
                    "variable_name": "Delivery fee",
                    "value": "NGN {}".format(fee)
                },
            ]
        }
    }
    response = requests.post(url, data=json.dumps(dataa), headers=headers)

    if response.status_code != 200:
        return str(response.status_code)

    return response.json()


def verify_payment(refrence):
    url = 'https://api.paystack.co/transaction/verify/{}'.format(refrence)
    headers = {
        'Authorization': PAYSTACK_SECRET_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return str(response.status_code)

    return response.json()


def create_subaccount(business_name, settlement_bank, account_number, percentage_charge):
    url = 'https://api.paystack.co/subaccount'
    headers = {
        'Authorization': PAYSTACK_SECRET_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    dataa = {
        "business_name": business_name,
        "settlement_bank": settlement_bank,
        "account_number": account_number,
        "percentage_charge": percentage_charge
    }

    response = requests.post(url, data=json.dumps(dataa), headers=headers)

    if response.status_code != 200:
        return response.json()

    return response.json()


def update_subaccount(subaccount_code, business_name, settlement_bank, account_number):
    url = 'https://api.paystack.co/subaccount/{}'.format(subaccount_code)
    headers = {
        'Authorization': PAYSTACK_SECRET_KEY,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    dataa = {
        "business_name": business_name,
        "settlement_bank": settlement_bank,
        "account_number": account_number,
    }

    response = requests.put(url, data=json.dumps(dataa), headers=headers)

    if response.status_code != 200:
        return response.json()

    return response.json()
