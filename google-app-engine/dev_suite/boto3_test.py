import os
os.environ['AWS_SHARED_CREDENTIALS_FILE'] = './cred'
import boto3

ip_list = []

ec2 = boto3.resource('ec2', region_name='us-east-1')
instances = ec2.create_instances(
    ImageId="ami-004bb14b6e31d8e7d",
    MinCount=1,
    MaxCount=1,
    InstanceType="t2.micro"
)
for instance in instances:
    instance.wait_until_running()
    instance.load()
    ip_list.append(instance.public_dns_name)
print("EC2 IPs: ", ip_list)
