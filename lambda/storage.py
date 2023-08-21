import json
import boto3
import csv

STORAGE_S3_BUCKET = "monte-carlo-analysis-bucket"


def lambda_handler(event, context):

    s3client = boto3.client('s3')
    body = json.loads(event['body'])
    print(body)
    if body['action'] == "store":
        obj = s3client.get_object(Bucket=STORAGE_S3_BUCKET, Key="audit.csv")
        lines = obj['Body'].read().decode('utf-8')
        data = [str(i) for i in body['data']]
        lines = lines + '\n' + ','.join(data)
        s3client.put_object(Bucket=STORAGE_S3_BUCKET,
                            Key="audit.csv", Body=lines.encode('utf-8'))
        return {"statusCode": 200}
    else:
        analysis_data = []
        obj = s3client.get_object(Bucket=STORAGE_S3_BUCKET, Key="audit.csv")
        rows = csv.DictReader(obj['Body'].read().decode('utf-8').split())
        for row in rows:
            analysis_data.append(row)
        return {
            "statusCode": 200,
            "body": analysis_data
        }
