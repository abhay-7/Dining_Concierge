import requests
from pprint import pprint
import json
url = "https://api.yelp.com/v3/businesses/search"
headers = {
    'content-type': "application/json",
    'authorization': "Bearer <Your Key>",
    'cache-control': "no-cache",
    'postman-token': "<Your taken>"
    }
ids=set()
dic=dict()
count=0
cuisines=["Indian","Chinese","Thai","Mexican","French","Japanese","American","Greek","Lebanese","Afghan","Irish"]
for item in cuisines:
    dic[item]=[]
    for offset in range(0,1000,50):
        print (offset)
        querystring = {"term":item,"location":"Manhattan","limit":50,"offset":offset}
        response = requests.request("GET", url, headers=headers, params=querystring)
        resp=json.loads(response.text)
        for items in resp["businesses"]:
            if (items["id"] not in ids):
                tmp=dict()
                count+=1
                ids.add(items["id"])
                tmp["id"]=items["id"]
                tmp["name"]=items["name"]
                tmp["review_count"]=items["review_count"]
                tmp["rating"]=items["rating"]
                tmp["coordinates"]=items["coordinates"]
                tmp["address"]=items["location"]["display_address"]
                tmp["zip_code"]=items["location"]["zip_code"]
                tmp["cuisine"]=item
                dic[item].append(tmp)
print ("Total Scrapped is =  "+str(count))
with open('scraped_data.json', 'w') as fp:
    json.dump(dic, fp,indent=4)