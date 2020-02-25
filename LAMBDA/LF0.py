import json
import boto3

def lambda_handler(event, context):
    # TODO implement
    lex = boto3.client('lex-runtime')
    # payload = json.loads(event['body'])
    incoming_msg = event['message']
    user_id = event['userId']
    bot_name = 'DiningConceirge'
    response = lex.post_text(
        botName=bot_name,
        botAlias=bot_name,
        userId=user_id,
        inputText=incoming_msg,
    )
    return {
        'statusCode': 200,
        'body': json.dumps(response['message'])
    }