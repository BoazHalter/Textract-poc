import boto3
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

def indexDocument(bucketName, objectName, text):

    # Update host with endpoint of your Elasticsearch cluster
    #host = "search--xxxxxxxxxxxxxx.us-east-1.es.amazonaws.com
    host = "https://vpc-textract-o5yvonnkr7avbxrlsq73xpc55a.eu-central-1.es.amazonaws.com"
    region = "eu-central-1"

    if(text):
        service = 'es'
        ss = boto3.Session()
        credentials = ss.get_credentials()
        region = ss.region_name

        awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

        es = Elasticsearch(
            hosts = [{'host': host, 'port': 443}],
            http_auth = awsauth,
            use_ssl = True,
            verify_certs = True,
            connection_class = RequestsHttpConnection
        )

        document = {
            "name": "{}".format(objectName),
            "bucket" : "{}".format(bucketName),
            "content" : text
        }

        es.index(index="textract", doc_type="document", id=objectName, body=document)

        print("Indexed document: {}".format(objectName))

def lambda_handler(event, context):
    s3_event = event['Records'][0]['s3']
    s3BucketName = s3_event['bucket']['name']
    documentName = s3_event['object']['key']
    # Amazon Textract client
    textract = boto3.client('textract')
    
    # Call Amazon Textract
    response = textract.detect_document_text(
        Document={
            'S3Object': {
                'Bucket': s3BucketName,
                'Name': documentName
            }
        })

    text = ""
    for item in response["Blocks"]:
        if item["BlockType"] == "LINE":
            print ('\033[94m' +  item["Text"] + '\033[0m')
            text += item["Text"]
    
    indexDocument(s3BucketName, documentName, text)

    # You can view index documents in Kibana Dashboard
    
