import requests

from services.STORAGE import GLOBAL_STATE
from config import STORAGE_LAMBDA_URL

GLOBAL_STATE_KEYS = GLOBAL_STATE.keys()


def set_state(data):
    for key in GLOBAL_STATE_KEYS:
        value = data.get(key)
        if value:
            GLOBAL_STATE[key] = value


def get_from_state(key):
    return GLOBAL_STATE.get(key)


def reset_state():
    set_state({"result": {"sell": [], "buy": [],
              "audit": {"avg_95": None, "avg_99": None, "profit_loss": None, "cost": None, "time": None, }}})


def store_audit_data_in_s3(data):
    data = [data["S"], data["R"], data["D"], data["H"], data["T"], data["P"],
            data["profit_loss"], data["avg_95"], data["avg_99"], data["time"], data["cost"]]
    requests.post(STORAGE_LAMBDA_URL, json={"action": "store", "data": data})


def get_audit_data_from_s3():
    data = requests.post(STORAGE_LAMBDA_URL, json={"action": "read"}).json()
    return data
