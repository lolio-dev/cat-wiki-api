from pprint import pprint

import requests
import json

from bson import ObjectId, json_util

url = "https://data.mongodb-api.com/app/data-glklp/endpoint/data/beta/action/find"
payload = json_util.dumps({
    "collection": "breeds_collection",
    "database": "db",
    "dataSource": "breeds-counter",
    "sort": {
        "views": -1
    }
})
headers = {
    'Content-Type': 'application/json',
    'Access-Control-Request-Headers': '*',
    'api-key': 'yZL7MkgbHzhs4JgxKU3fU4AFRhP7ASKnAk2beJ7E1vBdT4osvAynmiT2BfMjXNpL'
}
response = requests.post(url, headers=headers, data=payload)
pprint(response.json())
