import requests

token = "pk_95539169_SZWH0M6K10ZAK6B73S5MW4SUHZDATTI7"
response = requests.get(
    "https://api.clickup.com/api/v2/team",
    headers={"Authorization": token}
)
print(response.status_code)
print(response.json())