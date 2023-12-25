from opensearchpy import OpenSearch
import boto3

host = 'search-textract-open-search-yalghvqfy6ul5wb2vfz7ca6iku.eu-central-1.es.amazonaws.com'
port = 443
auth = () # For testing only. Don't store credentials in code.
#ca_certs_path = '/full/path/to/root-ca.pem' # Provide a CA bundle if you use intermediate CAs with your root CA.

# Define the mapping for your index based on the JSON structure
def create_index_mapping(client):
  
  index_mapping = {
      "mappings": {
          "properties": {
              "DocumentMetadata": {
                  "properties": {
                      "Pages": {"type": "integer"}
                  }
              },
              "Blocks": {
                  "type": "nested",
                  "properties": {
                      "BlockType": {"type": "keyword"},
                      "Geometry": {
                          "properties": {
                              "BoundingBox": {
                                  "properties": {
                                      "Width": {"type": "float"},
                                      "Height": {"type": "float"},
                                      "Left": {"type": "float"},
                                      "Top": {"type": "float"}
                                  }
                              },
                              "Polygon": {
                                  "type": "nested",
                                  "properties": {
                                      "X": {"type": "float"},
                                      "Y": {"type": "float"}
                                  }
                              }
                          }
                      },
                      "Id": {"type": "keyword"},
                      "Relationships": {
                          "type": "nested",
                          "properties": {
                              "Type": {"type": "keyword"},
                              "Ids": {"type": "keyword"}
                          }
                      },
                      "Confidence": {"type": "float"},
                      "Text": {"type": "text"},
                      "TextType": {"type": "keyword"},
                      "DetectDocumentTextModelVersion": {"type": "keyword"},
                      "ResponseMetadata": {
                          "properties": {
                              "RequestId": {"type": "keyword"},
                              "HTTPStatusCode": {"type": "integer"},
                              "HTTPHeaders": {
                                  "properties": {
                                      "x-amzn-requestid": {"type": "keyword"},
                                      "content-type": {"type": "keyword"},
                                      "content-length": {"type": "keyword"},
                                      "date": {"type": "date"}
                                  }
                              },
                              "RetryAttempts": {"type": "integer"}
                          }
                      }
                  }
              }
          }
      }
  }
  
  # Replace 'your_index_name' with the desired index name in your OpenSearch cluster
  index_name = 'textract-poc'
  
  # Create the index with the defined mapping
  client.indices.create(index=index_name, body=index_mapping)
  print(f"Index '{index_name}' created with the specified mapping.")


def initOpenSearchConnection():
  # Optional client certificates if you don't want to use HTTP basic authentication.
  # client_cert_path = '/full/path/to/client.pem'
  # client_key_path = '/full/path/to/client-key.pem'
  
  # Create the client with SSL/TLS enabled, but hostname verification disabled.
  client = OpenSearch(
      hosts = [{'host': host, 'port': port}],
      http_compress = True, # enables gzip compression for request bodies
      http_auth = auth,
      # client_cert = client_cert_path,
      # client_key = client_key_path,
      use_ssl = True,
      verify_certs = True,
      ssl_assert_hostname = False,
      ssl_show_warn = False
  )
  return client

def addDocumentToIndex(client,analyzed_doc):
  
  # Replace 'index_name' with the desired index name in your OpenSearch cluster
  index_name = 'textract-poc'
  id = '1'
  
  response = client.index(
      index = index_name,
      body = analyzed_doc,
      id = id,
      refresh = True
  )
  
  print('\nAdding document:')
  print(response)
  
  # Search for the document.
  q = 'miller'
  query = {
    'size': 5,
    'query': {
      'multi_match': {
        'query': q,
        'fields': ['title^2', 'director']
      }
    }
  }

  response = client.search(
      body = query,
      index = index_name
  )
  print('\nSearch results:')
  print(response)
  
def analyzedoc(s3BucketName,documentName):

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
  
  print(response)
  return response

def index_create():
  # Create an index with non-default settings.
  index_name = 'textract-poc'
  index_body = {
    'settings': {
      'index': {
        'number_of_shards': 4
      }
    }
  }
  
  response = client.indices.create(index_name, body=index_body)
  print('\nCreating index:')
  print(response)
  
def lambda_handler(event, context):
  s3_event = event['Records'][0]['s3']
  s3BucketName = s3_event['bucket']['name']
  documentName = s3_event['object']['key']
  #client = initOpenSearchConnection()
  #create_index_mapping(client)
  analyzed_doc = analyzedoc(s3BucketName,documentName)
  client = initOpenSearchConnection()
  addDocumentToIndex(client,analyzed_doc)
  
  
  
  ## Create an index with non-default settings.
  #index_name = 'textract-poc'
  #index_body = {
  #  'settings': {
  #    'index': {
  #      'number_of_shards': 4
  #    }
  #  }
  #}
  #
  #response = client.indices.create(index_name, body=index_body)
  #print('\nCreating index:')
  #print(response)


#
## Delete the document.
#response = client.delete(
#    index = index_name,
#    id = id
#)
#
#print('\nDeleting document:')
#print(response)
#
## Delete the index.
#response = client.indices.delete(
#    index = index_name
#)
#
#print('\nDeleting index:')
#print(response)
#
