import boto3
import time
import requests
from concurrent.futures import ThreadPoolExecutor

from config import AMI_ID, INSTANCE_NAME, EC2_FLASK_ENDPOINT

ec2 = boto3.resource('ec2', region_name='us-east-1')


def check_instance_availability(ip):
    while True:
        try:
            response = requests.get("http://" + ip + ":8080/")
            return {"ip": ip, "status": response.json()['status']}
        except requests.exceptions.ConnectionError as ex:
            time.sleep(2)
            continue


def create_instances(R):
    ip_list = []
    instance_ids = []
    ec2_status = {}
    instances = ec2.create_instances(
        ImageId=AMI_ID,
        MinCount=R,
        MaxCount=R,
        InstanceType="t2.micro"
    )
    for instance in instances:
        instance.wait_until_running()
        instance.load()
        ip_list.append(instance.public_dns_name)
        instance_ids.append(instance.id)
    print("EC2 IPs: ", ip_list)
    ec2.create_tags(Resources=instance_ids, Tags=[
                    {'Key': "Name", "Value": INSTANCE_NAME}])
    with ThreadPoolExecutor() as executor:
        results = executor.map(check_instance_availability, ip_list)
    for result in results:
        ec2_status[result['ip']] = result['status']
    return {"ip_list": ip_list, "ec2_status": ec2_status}


def run_ec2(ec2_data):
    ip = list(ec2_data.keys())[0]
    params = ec2_data[ip]
    response = requests.get("http://" + ip + ":8080/" +
                            EC2_FLASK_ENDPOINT, params=params)
    return response.json()


def terminate_instances():
    instances = ec2.instances.filter(
        Filters=[{'Name': 'tag:Name', 'Values': [INSTANCE_NAME]}])
    instances.terminate()
    return {"message": "EC2s terminated"}
