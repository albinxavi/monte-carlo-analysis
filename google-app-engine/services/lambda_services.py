import requests
from config import ANALYSE_LAMBDA_URL


def run_lambda(args):
    response = requests.post(ANALYSE_LAMBDA_URL, json=args)
    return response.json()


def get_cost(run_time):
    """ 
    The cost is calculated with the following assumptions and pricing

    --Unit conversions--
    Number of requests: 30 per hour * (730 hours in a month) = 21900 per month
    Amount of memory allocated: 256 MB x 0.0009765625 GB in a MB = 0.25 GB
    Amount of ephemeral storage allocated: 512 MB x 0.0009765625 GB in a MB = 0.5 GB
        --Pricing calculations--
    21,900 requests x 30,000 ms x 0.001 ms to sec conversion factor = 657,000.00 total compute (seconds)
    0.25 GB x 657,000.00 seconds = 164,250.00 total compute (GB-s)
    164,250.00 GB-s x 0.0000166667 USD = 2.74 USD (monthly compute charges)
    21,900 requests x 0.0000002 USD = 0.00 USD (monthly request charges)
    0.50 GB - 0.5 GB (no additional charge) = 0.00 GB billable ephemeral storage per function
    Lambda costs - Without Free Tier (monthly): 2.74 USD

    2.74 USD per month = 0.00000106 USD per second
    """
    cost = 0.00000106
    return run_time * cost
