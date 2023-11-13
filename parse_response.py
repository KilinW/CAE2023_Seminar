import json

# Read the response
with open("./response.json", "r") as f:
    response = json.load(f)

form = response['choices']['content']
print(form) 