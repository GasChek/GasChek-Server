import requests
import json


def initialize_payment(email, amount, callback_url, cylinder, gas_dealer):
    url = 'https://api.paystack.co/transaction/initialize'
    headers = {
        'Authorization': 'Bearer sk_test_ef9aabb495bedad40c86b3adc91778d48d16fb30',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    dataa = {
        "email": email,
        "amount": amount,
        "callback_url": callback_url,
        "metadata": {
            "custom_fields": [
                {
                    "display_name": "Cylinder",
                    "variable_name": "Cylinder",
                    "value": "{} kg".format(cylinder)
                },
                {
                    "display_name": "Gas Dealer",
                    "variable_name": "Gas Dealer",
                    "value": gas_dealer
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
        'Authorization': 'Bearer sk_test_ef9aabb495bedad40c86b3adc91778d48d16fb30',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return str(response.status_code)

    return response.json()
