import boto3
from boto3.dynamodb.conditions import Key, Attr
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer, Decimal

dynamodb = boto3.client('dynamodb')

def decimal_to_int(object):
    if isinstance(object, dict):
        return {
            k: decimal_to_int(v)
            for k, v in object.items()
        }
    elif isinstance(object, list):
        return [decimal_to_int(v) for v in object]
    elif isinstance(object, Decimal):
        return int(object)
    else:
        return object
def dynamodb_to_dict(dynamo_obj: dict) -> dict:
    deserializer = TypeDeserializer()
    result = {
        k: deserializer.deserialize(v)
        for k, v in dynamo_obj.items()
    }
    result = decimal_to_int(result)
    return result
def dict_to_dynamodb(python_obj: dict) -> dict:
    serializer = TypeSerializer()
    return {
        k: serializer.serialize(v)
        for k, v in python_obj.items()
    }

def create_item(table_name, dict_item):
    dynamodb_item = dict_to_dynamodb(dict_item)
    dynamodb.put_item(TableName = table_name, Item = dynamodb_item)
def read_item(table_name, dict_item):
    dynamodb_table = dynamodb.describe_table(TableName = table_name)['Table']
    partition_key = dynamodb_table['KeySchema'][0]['AttributeName']
    dynamodb_item = {}
    if partition_key in dict_item:
        dynamodb_item = dynamodb.get_item(TableName = table_name, Key = {partition_key: {'S': dict_item[partition_key]}})['Item']
    dict_item = dynamodb_to_dict(dynamodb_item)
    return dict_item
def read_items(table_name, dict_item):
    partition_key = ''
    secondary_index_key = ''
    secondary_index_name = ''
    unindexed_keys = []
    
    dynamodb_table = dynamodb.describe_table(TableName = table_name)['Table']
    if dynamodb_table['KeySchema'][0]['AttributeName'] in dict_item:
        partition_key = dynamodb_table['KeySchema'][0]['AttributeName']
    elif 'GlobalSecondaryIndexes' in dynamodb_table:
        for secondary_index in dynamodb_table['GlobalSecondaryIndexes']:
            if secondary_index['KeySchema'][0]['AttributeName'] in dict_item:
                secondary_index_name = secondary_index['IndexName']
                secondary_index_key = secondary_index['KeySchema'][0]['AttributeName']
                break
    for key in dict_item.keys():
        if key != partition_key and key != secondary_index_key:
            unindexed_keys.append(key)
    
    dynamodb_query = []
    if partition_key != '':
        result = dynamodb.query(
            TableName = table_name,
            KeyConditionExpression = partition_key + ' = :' + partition_key,
            ExpressionAttributeValues = {
                ':' + partition_key: {'S': dict_item[partition_key]}
            }
        )
        dynamodb_query = result['Items']
    elif secondary_index_key != '':
        result = dynamodb.query(
            TableName = table_name,
            IndexName = secondary_index_name,
            ExpressionAttributeValues = {
                ':' + secondary_index_key : {'S': dict_item[secondary_index_key]}
            },
            KeyConditionExpression = secondary_index_key + ' = :' + secondary_index_key
        )
        dynamodb_query = result['Items']
    else:
        result = dynamodb.scan(TableName = table_name)
        dynamodb_query = result['Items']
    
    dict_query = []
    for item in dynamodb_query:
        dict_query.append(dynamodb_to_dict(item))
        
    filtered_query = []
    for item in dict_query:
        match = True
        for key in unindexed_keys:
            if key in item:
                if item[key] != dict_item[key]:
                    match = False
                    break
            else:
                match = False
                break
        if match == True:
            filtered_query.append(item)
    return filtered_query
def update_item(table_name, dict_item):
    dynamodb.put_item(TableName = table_name, Item = dict_to_dynamodb(dict_item))
def delete_item(table_name, dict_item):
    dynamodb_table = dynamodb.describe_table(TableName = table_name)['Table']
    partition_key = dynamodb_table['KeySchema'][0]['AttributeName']
    if partition_key in dict_item:
        dynamodb.delete_item(TableName = table_name, Key = {partition_key: {'S': dict_item[partition_key]}})