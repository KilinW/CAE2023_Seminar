from openai import OpenAI
import pandas as pd
import base64
import requests
import os

image_id = 31
detail = "low"  # low, high

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
# Create result folder if not exist
if not os.path.exists("./result"):
    os.mkdir("./result")
if not os.path.exists("./result/response"):
    os.mkdir("./result/response")
if not os.path.exists("./result/label"):
    os.mkdir("./result/label")

# Read api key from file "token"
api_key = open("token.txt", "r").read()
img = encode_image(f"./ArcGIS_Dataset/ArcGIS_Dataset_images/id_000{image_id}.png")
prompt = open("./prompt.txt", "r").read()
df = pd.read_excel("./ArcGIS_Dataset/ArcGIS_Dataset.xlsx", sheet_name="ArcGIS_Dataset")

client = OpenAI(api_key=api_key)

def get_label(base64_image: str, api_key: str, prompt: str):
    '''
    base64_image : base64 encoded image
    '''
    # Packet information
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [
        {
            "role": "user",
            "content": [
            {
                "type": "text",
                "text": f"{prompt}"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}",
                    "detail": f"{detail}",
                }
            }
            ]
        }
        ],
        "max_tokens": 300
    }

    return requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

# Get the reply
response = get_label(img, api_key, prompt)
# Save the response as json in result folder
with open(f"./result/response/id_000{image_id}.json", "w") as f:
    f.write(response.text)
# Get the label form from the response
form = response.json()['choices'][0]['message']['content']
## Remove the heading '''json and trailing '''
#form = form[7:-3]
# Save the form as json in result folder
with open(f"./result/label/id_000{image_id}.json", "w") as f:
    f.write(form)