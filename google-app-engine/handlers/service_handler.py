import time
import json
import requests
from concurrent.futures import ThreadPoolExecutor

from services import lambda_services
from services import ec2_services
from services import storage_services
from services. STORAGE import GLOBAL_STATE
from config import ANALYSE_LAMBDA_URL


def warm_up(data):
    start_time = time.time()
    if data["s"] == "lambda":
        res = lambda_services.run_lambda(args={"warm_up": True})
    elif data["s"] == "ec2":
        res = ec2_services.create_instances(int(data['r']))
    end_time = time.time()
    data['warm_up_time'] = end_time-start_time
    storage_services.set_state(data)
    return res


def check_resources_ready():
    if storage_services.get_from_state('s') == "lambda":
        # since lambda is already warmed up it is already ready to serve the request
        lambda_services.run_lambda(args={"warm_up": True})
        res = {'warm': True}
    elif storage_services.get_from_state('s') == "ec2":
        res = ec2_services.check_instances_ready(
            storage_services.get_from_state('instance_urls'))
    elif storage_services.get_from_state('s') == None:
        return {"error": "No resources have been warmed up/created in this session"}
    else:
        res = {"error": "invalid value for s"}
    return res


def get_warmup_cost():
    S = storage_services.get_from_state('s')
    warm_up_time = storage_services.get_from_state('warm_up_time')
    cost = lambda_services.get_cost(
        warm_up_time) if S == "lambda" else ec2_services.get_cost(warm_up_time)
    res = {
        'time': warm_up_time,
        'cost': cost
    }
    return res


def get_endpoints():
    if storage_services.get_from_state('s') == "lambda":
        # there is only one instance of lambda
        call_strings = [ANALYSE_LAMBDA_URL]
    elif storage_services.get_from_state('s') == "ec2":
        call_strings = [storage_services.get_from_state('instance_urls')]
    elif storage_services.get_from_state('s') == None:
        return {"error": "No resources have been warmed up/created in this session"}
    else:
        return {"error": "Invalid value for s"}
    return {"resources": call_strings}


def analyse(args):
    S = storage_services.get_from_state('s')
    R = int(storage_services.get_from_state('r'))
    D, H, P, T = int(args.get('d')), int(
        args.get('h')), int(args.get('p')), args.get('t')
    req_json = {"d": D, "h": H, "p": P, "t": T, "warm_up": False
                }
    storage_services.set_state(req_json)

    data = []
    result = {"sell": [], "buy": [], "audit": {}}
    start_time = time.time()
    if S == "lambda":
        with ThreadPoolExecutor() as executor:
            response = executor.map(lambda_services.run_lambda, [req_json]*R)
    elif S == "ec2":
        ec2_data = []
        ip_list = storage_services.get_from_state('instance_urls')
        for ip in ip_list:
            ec2_data.append({ip: req_json})
        with ThreadPoolExecutor() as executor:
            response = executor.map(ec2_services.run_ec2, ec2_data)
    else:
        return {"error": "Invalid value for s"}

    for res in response:
        data.append(res)

    signal_key = 'buy_results' if args.get('t') == 'buy' else 'sell_results'
    PoL_list = []
    for i in range(len(data[0][signal_key])):
        sum_95, sum_99, PoL = 0, 0, 0
        for j in range(R):
            sum_95 += data[j][signal_key][i][0]
            sum_99 += data[j][signal_key][i][1]
            PoL += data[j][signal_key][i][2]
        result[T].append([sum_95/R, sum_99/R, PoL])
        PoL_list.append(PoL)
    avg_result = [sum(x)/len(x) for x in zip(*result[T])]
    end_time = time.time()

    run_time = end_time-start_time
    cost = lambda_services.get_cost(
        run_time) if S == "lambda" else ec2_services.get_cost(run_time)

    result['audit'] = {"S": S, "R": R, "D": D, "H": H, "P": P, "T": T,
                       "avg_95": avg_result[0], "avg_99": avg_result[1], "profit_loss": sum(PoL_list), "time": end_time-start_time, "cost": cost}
    storage_services.set_state({"result": result})
    storage_services.store_audit_data_in_s3(result['audit'])
    return {"result": "ok"}


def get_sig_vars9599():
    signal_key = storage_services.get_from_state('t')
    sig_vars = storage_services.get_from_state('result')[signal_key]
    res = {
        'var95': [result[0] for result in sig_vars],
        'var99': [result[1] for result in sig_vars]
    }
    return res


def get_avg_vars9599():
    res = {
        'var95': storage_services.get_from_state('result')['audit']['avg_95'],
        'var99': storage_services.get_from_state('result')['audit']['avg_99']
    }
    return res


def get_sig_profit_loss():
    signal_key = storage_services.get_from_state('t')
    sig_vars = storage_services.get_from_state('result')[signal_key]
    res = {'profit_loss': [result[2] for result in sig_vars]}
    return res


def get_tot_profit_loss():
    res = {
        'profit_loss': storage_services.get_from_state('result')['audit']['profit_loss']
    }
    return res


def get_chart_url():
    signal_key = storage_services.get_from_state('t')
    sig_vars = storage_services.get_from_state('result')[signal_key]
    chart_data = {"chart": {
        "type": "bar",
        "data": {
            "labels": [""] * len(sig_vars),
            "datasets": [
                {
                    "type": "line",
                    "label": "95% risk",
                    "fill": "false",
                    "borderWidth": 2,
                    "data": [result[0] for result in sig_vars]
                },
                {
                    "type": "line",
                    "label": "99% risk",
                    "fill": "false",
                    "borderWidth": 2,
                    "data": [result[1] for result in sig_vars]
                },
                {
                    "type": "line",
                    "label": "Average 95% risk",
                    "fill": "false",
                    "borderWidth": 2,
                    "data": [storage_services.get_from_state('result')['audit']['avg_95']] * len(sig_vars)
                },
                {
                    "type": "line",
                    "label": "Average 99% risk",
                    "fill": "false",
                    "borderWidth": 2,
                    "data": [storage_services.get_from_state('result')['audit']['avg_99']] * len(sig_vars)
                }
            ]}
    }}
    response = requests.post(
        "https://quickchart.io/chart/create", json=chart_data)
    url = json.loads(response.text)["url"]

    return {"url": url}


def get_time_cost():
    res = {
        'time': storage_services.get_from_state('result')['audit']['time'],
        'cost': storage_services.get_from_state('result')['audit']['cost']
    }
    return res


def get_audit():
    data = storage_services.get_audit_data_from_s3()
    return {"audit_data": data}


def reset():
    storage_services.reset_state()
    return {"result": "ok"}


def terminate():
    if storage_services.get_from_state('s') == "lambda":
        # lambda is not terminated
        res = {"result": "ok"}
    elif storage_services.get_from_state('s') == "ec2":
        res = ec2_services.terminate_instances()
    elif storage_services.get_from_state('s') == None:
        return {"error": "No resources have been warmed up/created in this session"}
    else:
        return {"error": "Invalid value for s"}
    return res


def check_resources_terminated():
    if storage_services.get_from_state('s') == "lambda":
        # lambda is not terminated
        res = {"terminated": True}
    elif storage_services.get_from_state('s') == "ec2":
        res = ec2_services.check_instances_terminated()
    elif storage_services.get_from_state('s') == None:
        return {"error": "No resources have been warmed up/created in this session"}
    else:
        return {"error": "Invalid value for s"}
    return res
