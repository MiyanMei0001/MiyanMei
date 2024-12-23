import requests
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description='Process image through API')
    parser.add_argument('--image_url', type=str, required=True, help='URL of the image to process')
    return parser.parse_args()

def main():
    args = parse_args()
    
    api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYyMTY3NzA2LCJpYXQiOjE3MzA2MzE3MDYsImp0aSI6IjVuMkFPMW5kIiwidXNlcl9pZCI6NDQ3Nn0.6_pDVtC5YDN26XXG31kxxT6sMlDkkm1zVzO0CIy9OqM"
    request = {
        "inputs": {
            "image": args.image_url
        }
    }

    response = requests.post(
        "https://youml.com/api/v1/recipes/5968/run?wait=600",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        },
        json=request,
        allow_redirects=True,
        timeout=90)

    result = response.json()
    values = []
    
    def find_values(data):
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "value" and isinstance(value, str):
                    values.append(value)
                find_values(value)
        elif isinstance(data, list):
            for item in data:
                find_values(item)

    find_values(result)
    print(values[1])

if __name__ == "__main__":
    main()