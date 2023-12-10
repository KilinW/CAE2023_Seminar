from openai import OpenAI
import pandas as pd
import base64
import requests
import json
import os

image_folder = './Development_Dataset/Development_Dataset_Images/'
images = os.listdir(image_folder)
api_key = open("token.txt", "r").read()
prompt = open("./prompt.txt", "r").read()

# Create result folder if not exist
if not os.path.exists("./result"):
    os.mkdir("./result")
if not os.path.exists("./result/response"):
    os.mkdir("./result/response")
if not os.path.exists("./result/label"):
    os.mkdir("./result/label")

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# Evaluate the image
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
                    "detail": "low",
                }
            }
            ]
        }
        ],
        "max_tokens": 300
    }

    return requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

if __name__ == "__main__":
    for image in images:
        # Trim the extension by spliting the string so it is robust to any extension
        img_b64 = encode_image(image_path=image_folder+image)
        # Get the reply
        try:
            response = get_label(img_b64, api_key, prompt)
        except:
            print(f"Error in {image}")
            print(f'Error while getting response from API')
            continue


        try:
            # Save the response as json in result folder
            with open(f"./result/response/{image.split('.')[0]}.json", "w") as f:
                f.write(response.text)
            # Get the label form from the response
            form = response.json()['choices'][0]['message']['content']
            ## Remove the heading '''json and trailing '''
            #form = form[7:-3]
            # Save the form as json in result folder
            with open(f"./result/label/{image.split('.')[0]}.json", "w") as f:
                f.write(form)
        except:
            print(f"Error in {image}")
            print(response)
            continue

    # Read result folder
    result = os.listdir("./result/label")
    # Create a dataframe with metadata columns
    df_list = []
    for image in result:
        # Trim the extension by spliting the string so it is robust to any extension
        image = image.split('.')[0]
        # Read the json file
        with open(f"./result/label/{image}.json", "r") as f:
            # Load json
            label = json.load(f)
            label['ImageID'] = image
        # Convert label as a dataframe
        label = pd.DataFrame(label, index=[0], dtype=str)
        df_list.append(label)
        
    # Concatenate all the dataframe with dtype str
    df = pd.concat(df_list, ignore_index=True)

    # Move the ImageID column to the first column
    cols = list(df)
    cols.insert(0, cols.pop(cols.index('ImageID')))
    df = df.loc[:, cols]

    # Save the dataframe as csv
    df.to_csv("./label.csv", index=False)
    # Replace all True/False/None to Y/N/U
    df = df.replace({'True': 'Y', 'False': 'N', None: 'U'})
    # Save the dataframe as csv
    df.to_csv("./label.csv", index=False)