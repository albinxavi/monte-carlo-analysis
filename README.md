# Monte-carlo risk analysis using GAE and AWS resources

#### The application is hosted in GAE and interacts with AWS resources over https and via boto3 SDK.
#### For persisting storage across users and sessions an s3 bucket is used.
#### Credential issue is faced when interacting with AWS resources via boto3 SDK.
#### The calls have been mediated through Lambda to resolve the credential issue, but in case of operations on ec2 the provided role "LabRole" doesn't have permissions. Therefore the creds file in the GAE needs to be updated to perform any API calls relating to ec2.

## The parameters for for the application is given below:

GAE HOST = monte-carlo-analysis-395818.nw.r.appspot.com

ANALYSE_LAMBDA_URL = https://234tauunniu7dpf35qk4t4uoya0wtgiy.lambda-url.us-east-1.on.aws/

STORAGE_LAMBDA_URL = https://5aywhajztd6up5ymjkqyhf6nva0shsxs.lambda-url.us-east-1.on.aws/

STORAGE_S3_BUCKET = monte-carlo-analysis-bucket

AMI_ID = ami-0730e426690d2ff98

## All the cURL requests to the application are as follows 

### warmup (post)
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/warmup' \
--header 'Content-Type: application/json' \
--data '{
    "s": "lambda",
    "r": 1
}'

### resources_ready
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/resources_ready'

### get_warmup_cost
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/get_warmup_cost'

### get_endpoints
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/get_endpoints'

### analyse (post)
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/analyse' \
--header 'Content-Type: application/json' \
--data '{
    "d": 10000,
    "h": 101,
    "t": "sell",
    "p": 7
}'

### get_sig_vars9599
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/get_sig_vars9599'

### get_avg_vars9599
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/get_avg_vars9599'

### get_sig_profit_loss
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/get_sig_profit_loss'

### get_tot_profit_loss
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/get_tot_profit_loss'

### get_chart_url
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/get_chart_url'

### get_time_cost
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/get_time_cost'

### get_audit
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/get_audit'

### reset
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/reset'

### terminate
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/terminate'

### resources_terminated
curl --location 'https://monte-carlo-analysis-395818.nw.r.appspot.com/resources_terminated'
