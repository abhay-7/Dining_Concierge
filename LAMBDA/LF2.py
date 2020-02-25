import json
from botocore.vendored import requests
import boto3
import random
def lambda_handler(event, context):
    # TODO implement
    client = boto3.client('sqs')
    response = client.receive_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/098015424271/Q1',AttributeNames=["ALL"])
    URL = "https://search-restaurants-5la4bfo7xuffrslg2yawxdr33u.us-east-1.es.amazonaws.com/restaurants/_search"
    header={"Content-Type":"application/json"}
    #print (response["Messages"][0]["Body"])
    #print (response)
    tmp=json.loads(response["Messages"][0]["Body"])
    message = response['Messages'][0]
    receipt_handle = message['ReceiptHandle']
    cuisine=tmp["cuisine"]
    query = {"size":1000 ,"query": {"match": {"cuisine":cuisine}}}
    response = requests.get(URL, data = json.dumps(query),headers = header)
    dat=json.loads(response.text)
    es=dat["hits"]["hits"]
    client2 = boto3.client('dynamodb',region_name="us-east-2")
    # Hello! Here are my Japanese restaurant suggestions for 2 people, for today at 7 pm: 1.
    # Sushi Nakazawa, located at 23 Commerce St, 2. Jin Ramen, located at 3183 Broadway,
    # 3. Nikko, located at 1280 Amsterdam Ave. Enjoy your meal!
    phone=str(tmp["phone"])
    if (phone.startswith("+1")):
        pass
    else:
        phone="+1"+str(tmp["phone"])
    template="Hello! Here are my "+str(cuisine)+" restaurant suggestions for "+str(tmp["people"])+" people, for "+str(tmp["date"])+" at "+str(tmp["time"])+":"
    for i in range(3):
        n=random.randrange(len(es))
        id_f=es[n]["_id"]
        response = client2.get_item(TableName='yelp-restaurants',Key={"id":{"S":id_f }})
        #print (response)
        template=template+str(i+1)+") "+response["Item"]["name"]["S"]+", located at "+str(response["Item"]["address"]["S"])+"; "
        print (response["Item"]["name"]["S"])
        print (response["Item"]["address"]["S"])
    template=template[:-2]+". Enjoy Your Meal!!"
    print (template)
    client3 = boto3.client('sns')
    response=client3.publish(PhoneNumber=phone,Message=template)
    print(response)
    client.delete_message(QueueUrl='https://sqs.us-east-1.amazonaws.com/098015424271/Q1',ReceiptHandle=receipt_handle)
    return {
        'statusCode': 200,
        'body': json.dumps('Invocation Succesfull')
    }
