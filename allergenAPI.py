import json
import boto3

dynamodb = boto3.resource('dynamodb')
table_name = 'ProductAllergenInfo'

#declaring two methods GET and POST

def lambda_handler(event, context):
    print("Received event:", json.dumps(event))
    http_method = event['httpMethod']
    
    if http_method == 'GET':
        return get_product_allergen_info(event)
    elif http_method == 'POST':
        return add_product_allergen_info(event)
    else:
        return {
            "statusCode": 405,
            "body": json.dumps({"message": "Method Not Allowed"}),
            "headers": {
                "Content-Type": "application/json"
            }
        }
#specifying the function of two methods GET and POST

def product_allergen_info(event, context):
    if event['httpMethod'] == 'GET':
        return get_product_allergen_info(event)
    elif event['httpMethod'] == 'POST':
        return add_product_allergen_info(event)
    else:
        return {
            "statusCode": 405,
            "body": json.dumps({"message": "Method Not Allowed"}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

# lambda function to trigger allergen infor
def get_product_allergen_info(event):
    product_id = event['queryStringParameters']['product_id']
    
    table = dynamodb.Table(table_name)
    response = table.get_item(Key={'product_id': product_id})
    
    if 'Item' in response:
        allergen_info = response['Item']
        return {
            "statusCode": 200,
            "body": json.dumps(allergen_info),
            "headers": {
                "Content-Type": "application/json"
            }
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"message": "Allergen information not found for the product"}),
            "headers": {
                "Content-Type": "application/json"
            }
        }

def add_product_allergen_info(event):
    # Parse request body
    body = json.loads(event['body'])
    product_id = body['product_id']
    product_name = body['product_name']
    allergens = body['allergens']
    cross_contamination_risks = body['cross_contamination_risks']
    labeling_information = body['labeling_information']
    
    # Store allergen details in DynamoDB
    table = dynamodb.Table(table_name)
    table.put_item(
        Item={
            'product_id': product_id,
            'product_name': product_name,
            'allergens': allergens,
            'cross_contamination_risks': cross_contamination_risks,
            'labeling_information': labeling_information
        }
    )
    
    # Return success response
    return {
        "statusCode": 200,
        "body": json.dumps({"message": "Allergen details added successfully"}),
        "headers": {
            "Content-Type": "application/json"
        }
    }