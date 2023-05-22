import time
from concurrent.futures import ThreadPoolExecutor

from services import lambda_services
from services import ec2_services
from services import db_services


def warm_up_lambda():
    return lambda_services.run_lambda(args={"warm_up": True})


def provision_ec2(R):
    return ec2_services.create_instances(int(R))


def store_analaysis_to_db(data):
    query = f'INSERT INTO AUDIT(S, R, H, D, P, T, PROFITORLOSS, NINETYFIVEAVG, NINETYNINEAVG, COST) VALUES(\'{data["S"]}\', {data["R"]}, {data["H"]}, {data["D"]}, {data["P"]}, \'{data["T"]}\', {data["avg_PoL"]}, {data["avg_95"]}, {data["avg_99"]}, {data["cost"]})'
    print(query)
    db_services.execute_query(query)


def simulate(args):
    S = args.get('S')
    R = int(args.get('R'))
    D, H, P, T = int(args.get('D')), int(
        args.get('H')), int(args.get('P')), args.get('T')
    req_json = {"D": D, "H": H, "P": P, "T": T, "warm_up": False
                }
    data = []
    response = {"sell_results": [], "buy_results": [], "audit_result": {}}
    start_time = time.time()
    if S == "lambda":
        with ThreadPoolExecutor() as executor:
            results = executor.map(lambda_services.run_lambda, [req_json]*R)
    else:
        ec2_data = []
        ip_list = args.get("ipList")
        for ip in ip_list:
            ec2_data.append({ip: req_json})
        with ThreadPoolExecutor() as executor:
            results = executor.map(ec2_services.run_ec2, ec2_data)

    for result in results:
        data.append(result)

    signal_key = 'buy_results' if args.get('T') == 'Buy' else 'sell_results'
    for i in range(len(data[0][signal_key])):
        sum_95, sum_99, PoL = 0, 0, 0
        for j in range(R):
            sum_95 += data[j][signal_key][i][0]
            sum_99 += data[j][signal_key][i][1]
            PoL += data[j][signal_key][i][2]
        response[signal_key].append([sum_95/R, sum_99/R, PoL/R])
    avg_result = [sum(x)/len(x) for x in zip(*response[signal_key])]
    end_time = time.time()

    response['audit_result'] = {"S": S, "R": R, "D": D, "H": H, "P": P, "T": T,
                                "avg_95": avg_result[0], "avg_99": avg_result[1], "avg_PoL": avg_result[2], "cost": end_time-start_time}

    store_analaysis_to_db(response['audit_result'])
    return response


def terminate_EC2s():
    return ec2_services.terminate_instances()
