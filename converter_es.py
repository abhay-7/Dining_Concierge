import os
import json
f1=open("bulk_restaurants.json","w")
with open('scraped_data.json') as json_file:
    data = json.load(json_file)
    for item in data:
        print (item)
        for i in data[item]:
            tmp={ "index": { "_index" : "restaurants","_type" : "_doc", "_id" : i["id"]}}
            f1.write(json.dumps(tmp))
            f1.write("\n")
            doc=dict()
            doc["cuisine"]=item
            f1.write(json.dumps(doc))
            f1.write("\n")

f1.close()