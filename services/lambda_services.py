import requests

ANALYSE_LAMBDA_URL = "https://phhxobp6pyjwt3txssqoxnxzh40bvipr.lambda-url.us-east-1.on.aws/"


def run_lambda(args):
    response = requests.post(ANALYSE_LAMBDA_URL, json=args)
    return response.json()
