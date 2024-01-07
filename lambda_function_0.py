from opensearchpy import OpenSearch
import boto3
import time
import json
import os
from datetime import datetime  



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
  
  host = 'search-textract-open-search-yalghvqfy6ul5wb2vfz7ca6iku.eu-central-1.es.amazonaws.com'
  port = 443
  auth = ('', '') # For testing only. Don't store credentials in code.

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

                      
def addDocumentToIndex(client,analyzed_doc,documentName,text,s3BucketName):
  
  # Replace 'index_name' with the desired index name in your OpenSearch cluster
  index_name = 'textract-poc'
  current_datetime = datetime.now()
  id = str(documentName) +"-"+ str(current_datetime)
  
  with open(analyzed_doc, 'r') as file:
        data = file.read()

  response_0 = client.index(
      index = index_name,
      body = data,
      id = id+"json",
      refresh = True
  )
  document = {
        "name": "{}".format(id),
        "bucket" : "{}".format(s3BucketName),
        "content" : text
  }

  response_1 = client.index(index=index_name, id=id+"text" , body=document)
  print("Indexed document: {}".format(id))

  print('\nAdding document:')
  print(response_0)
  print(response_1)
  
  # Search for the document.
  #q = 'miller'
  #query = {
  #  'size': 5,
  #  'query': {
  #    'multi_match': {
  #      'query': q,
  #      'fields': ['title^2', 'director']
  #    }
  #  }
  #}
#
  #response = client.search(
  #    body = query,
  #    index = index_name
  #)
  #print('\nSearch results:')

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
  
  text = ""
  for item in response["Blocks"]:
     if item["BlockType"] == "LINE":
        print ('\033[94m' +  item["Text"] + '\033[0m')
        text += item["Text"]
  return response ,text

def index_create(client):
  # Create an index with non-default settings.
  index_name = 'textract-poc-0'
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

def save_response_to_file(response, output_file_path):
    # Write the AWS Textract response to a JSON file
    with open(output_file_path, 'w') as output_file:
        json.dump(response, output_file, indent=4)
    print(f"Response saved to '{output_file_path}'")


def lambda_handler(event, context):
  
  s3_event = event['Records'][0]['s3']
  s3BucketName = s3_event['bucket']['name']
  documentName = s3_event['object']['key']
  file_path = '/tmp/blocks_data.json'
  
  if os.path.exists(file_path):
      print(f"The file {file_path} exists. Deleting...")
      os.remove(file_path)
      print(f"The file {file_path} has been deleted.")
  else:
      print(f"The file {file_path} does not exist.")

  #client = initOpenSearchConnection()
  #create_index_mapping(client)
  
  analyzed_doc = analyzedoc(s3BucketName,documentName)
  print("-----------")
  # Example usage:
  
  
  save_response_to_file(analyzed_doc[0], file_path)
  client = initOpenSearchConnection()
  #index_create(client)
  addDocumentToIndex(client,file_path,documentName,analyzed_doc[1],s3BucketName)
  print("-----------")
  
  
  
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
