import boto3

def lambda_handler(event, context):
    # Initialize the Textract client
    textract_client = boto3.client('textract')

    # S3 bucket and object key where the image is stored
    bucket_name = 'your-bucket-name'
    object_key = 'path/to/your/image.jpg'  # Replace with the image path in your bucket

    # Call Textract to analyze text within the image
    response = textract_client.detect_document_text(
        Document={
            'S3Object': {
                'Bucket': bucket_name,
                'Name': object_key
            }
        }
    )

    # Extract text detected by Textract
    detected_text = ''
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            detected_text += item['Text'] + '\n'

    return {
        'statusCode': 200,
        'body': detected_text
    }
