import os
import json
from datetime import datetime
d={"yelp-restaurants":[]}
tmp={"PutRequest":{"Item":{}}}
c=1
cnt=1
with open('scraped_data.json') as json_file:
    data = json.load(json_file)
    for item in data:
        print (item)
        for i in data[item]:
            if(cnt<25):
                tmp["PutRequest"]["Item"]["Category"]={"S":item}
                now = datetime.now()
                dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                tmp["PutRequest"]["Item"]["insertedAtTimestamp"]={"S":dt_string}
                tmp["PutRequest"]["Item"]["id"]={"S":i["id"]}
                tmp["PutRequest"]["Item"]["name"]={"S":str(i["name"])}
                tmp["PutRequest"]["Item"]["review_count"]={"N":str(i["review_count"])}
                tmp["PutRequest"]["Item"]["rating"]={"S":str(i["rating"])}
                tmp["PutRequest"]["Item"]["zip_code"]={"N":str(i["zip_code"])}
                tmp["PutRequest"]["Item"]["longitude"]={"S":str(i["coordinates"]["longitude"])}
                tmp["PutRequest"]["Item"]["latitude"]={"S":str(i["coordinates"]["latitude"])}
                st=""
                for items in i["address"]:
                    st=st+items+" "
                tmp["PutRequest"]["Item"]["address"]={"S":st}
                d["yelp-restaurants"].append(tmp)
                tmp={"PutRequest":{"Item":{}}}
                cnt+=1
            else :
                with open('data/yelp-restaurants'+str(c)+'.json', 'w') as outfile:
                    json.dump(d, outfile,indent=4)
                c+=1
                cnt=1
                d={"yelp-restaurants":[]}
                tmp={"PutRequest":{"Item":{}}}

with open('data/yelp-restaurants'+str(c)+'.json', 'w') as outfile:
    json.dump(d, outfile,indent=4)
