import argparse
import pytesseract
from PIL import Image
import requests
from io import BytesIO

def download_image(url):
    response = requests.get(url)
    response.raise_for_status()  # Check if the request was successful
    return Image.open(BytesIO(response.content))

def perform_ocr(image):
    return pytesseract.image_to_string(image)

def main():
    parser = argparse.ArgumentParser(description="OCR script to extract text from an image URL.")
    parser.add_argument("url", type=str, help="URL of the image to process")
    args = parser.parse_args()

    try:
        image = download_image(args.url)
        text = perform_ocr(image)
        print(text)
        return text
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()