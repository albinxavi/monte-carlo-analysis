import boto3
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from services import storage_services

from config import AMI_ID, INSTANCE_NAME, EC2_FLASK_ENDPOINT

ec2 = boto3.resource('ec2', region_name='us-east-1')


def check_instance_availability(instance_url):
    while True:
        try:
            response = requests.get(instance_url)
            return {"instance_url": instance_url, "status": response.json()['status']}
        except requests.exceptions.ConnectionError as ex:
            time.sleep(2)
            continue


def check_instances_ready(instance_urls):
    if len(instance_urls) == 0:
        # if there is no ip in the list return error
        return {"error": "No ec2 in the list!"}
    for instance_url in instance_urls:  # for each ip in the list check if the ec2 server is running
        try:
            response = requests.get(instance_url)
            if response.status_code != 200:
                return {'warm': False}
        except requests.exceptions.ConnectionError:
            return {'warm': False}
    # return true if none of the negative conditions were satisfied
    return {'warm': True}


def create_instances(r):
    instance_urls = []
    instance_ids = []
    instances = ec2.create_instances(
        ImageId=AMI_ID,
        MinCount=r,
        MaxCount=r,
        InstanceType="t3.micro"
    )
    for instance in instances:
        instance.wait_until_running()
        instance.load()
        instance_urls.append(instance.public_dns_name)
        instance_ids.append(instance.id)
    print("EC2 IPs: ", instance_urls)
    ec2.create_tags(Resources=instance_ids, Tags=[
                    {'Key': "Name", "Value": INSTANCE_NAME}])
    storage_services.set_state(
        {'instance_urls': ["http://" + instance_url + ":8080/" for instance_url in instance_urls]})
    return {"result": "ok"}


def run_ec2(ec2_data):
    intance_url = list(ec2_data.keys())[0]
    params = ec2_data[intance_url]
    response = requests.post(intance_url +
                             EC2_FLASK_ENDPOINT, json=params)
    return response.json()


def terminate_instances():
    instances = ec2.instances.filter(
        Filters=[{'Name': 'tag:Name', 'Values': [INSTANCE_NAME]}])
    instances.terminate()
    return {"result": "ok"}


def check_instances_terminated():
    instances = ec2.instances.filter(
        Filters=[{'Name': 'tag:Name', 'Values': [INSTANCE_NAME]}, {'Name': 'instance-state-name', 'Values': ['running']}])
    for instance in instances:
        print(instance)
        return {"terminated": False}        
    return {"terminated": True}


def get_cost(run_time):
    """ 
    The cost is calculated with that 5 instances will be running throughout a month.
    This is a calulated average point since our instances would be put to use for only a few minutes.

    5 instances x 0.0104 USD On Demand hourly cost x 730 hours in a month = 37.960000 USD
    On-Demand instances (monthly): 37.960000 USD

    37.960000 USD = USD per second
    """
    cost = 0.00001444
    return run_time * cost
