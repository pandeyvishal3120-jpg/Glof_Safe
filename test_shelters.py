import requests

query = r'''
[out:json][timeout:40];
nwr(around:10000,30.65,80.35)["emergency"="assembly_point"];
out center tags;
'''

headers = {
    "User-Agent": "GLOF-SAFE/1.0"
}

r = requests.post(
    "https://overpass-api.de/api/interpreter",
    data={"data": query},
    headers=headers,
    timeout=60
)

print("STATUS:", r.status_code)
print(r.text[:5000])
