import requests
from config import LAMBDA_URL


def run_lambda(args):
    response = requests.post(LAMBDA_URL, json=args)
    return response.json()
