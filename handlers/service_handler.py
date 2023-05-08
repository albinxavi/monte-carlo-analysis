from concurrent.futures import ThreadPoolExecutor

from services import lambda_services
from services import ec2_services


def warm_up_lambda():
    return lambda_services.run_lambda(args={"warm_up": True})


def provision_ec2(R):
    return ec2_services.create_instances(int(R))


def simulate(args):
    S = args.get('S')
    R = int(args.get('R'))
    req_json = {
        "D": int(args.get('D')),
        "H": int(args.get('H')),
        "P": int(args.get('P')),
        "T": args.get('T'),
        "warm_up": False
    }
    if S == "lambda":
        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda_services.run_lambda, [req_json]*R)
        for result in results:
            print(result)
        return {
            "test": "lambda"
        }
    else:
        ec2_data = []
        ip_list = args.get("ipList")
        for ip in ip_list:
            ec2_data.append({ip: req_json})
        print(ec2_data)
        with ThreadPoolExecutor() as executor:
            results = executor.map(ec2_services.run_ec2, ec2_data)
        for result in results:
            print(result)
        return {
            "test": "ec2"
        }
