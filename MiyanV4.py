# Library
import asyncio
import aiohttp
import os
import subprocess
import sys
import json
import requests
import time
import random
import re
import uuid
import threading
import pandas
import shutil
import tempfile
import hypercorn.asyncio
import urllib.request
import urllib.parse
import urllib.error
import urllib.response
import urllib.robotparser
import numpy as np
import google.generativeai as genai
from quart import *
from google.generativeai.types import *
from PIL import Image
from pytubefix import YouTube, Search
from pytubefix.cli import on_progress
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from booru import *
from playwright.async_api import async_playwright
from hypercorn.config import Config
from datetime import datetime

# Variable
app = Quart(__name__)
app.config['DEBUG'] = False
app.config['ENV'] = 'production'
app.config['PROPAGATE_EXCEPTIONS'] = False
genai.configure(api_key='AIzaSyDb27FVEnAlJkbZVP15lapXAig3Gf7NMeI')
cs_apikey = "AIzaSyC1AkyH5_qssVVbPYXY5BOxdE9h1JHM0Mw"
cx_id = "e2abed52db8a3468f"
gemini_default_model = "gemini-1.5-flash-8b"
ai_history = {}
blackbox_history = {}

# Function
async def randomUUID():
    return str(uuid.uuid4())

async def tourl(path):
    url = "https://uguu.se/upload.php"
    
    payload = {
        'files[]': open(path, 'rb')
    }
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 11; Infinix X6511B Build/RP1A.201005.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.39 Mobile Safari/537.36",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'sec-ch-ua-platform': "\"Android\"",
        'sec-ch-ua': "\"Android WebView\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        'sec-ch-ua-mobile': "?1",
        'origin': "https://uguu.se",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://uguu.se/",
        'accept-language': "en,en-US;q=0.9",
        'priority': "u=1, i"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers) as response:
            response_json = await response.json()
            file_url = response_json['files'][0]['url']
            return file_url

async def upload_to_gemini(path):
    file = genai.upload_file(path)
    return file

async def wait_for_files_active(files):
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            await asyncio.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")

async def fetch_page(session, url):
    async with session.get(url) as response:
        return await response.text()

async def html_to_image(text):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        path = f"{await randomUUID()}.png"
        await page.set_content(text)
        await page.screenshot(path=path)
        await browser.close()
        return path
        
async def html_to_video(text, duration=5):
    try:
        # Create a temporary directory
        with tempfile.TemporaryDirectory() as video_dir:
            async with async_playwright() as p:
                # Launch browser with video recording context
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    record_video_dir=os.path.abspath(video_dir),
                )
                
                # Create a new page
                page = await context.new_page()
                
                # Set page content
                await page.set_content(text)
                
                # Wait for the specified duration
                await page.wait_for_timeout(duration * 1000)
                
                # Close page and browser
                await page.close()
                await context.close()
                await browser.close()
                
                # Find the generated video file
                video_files = os.listdir(video_dir)
                if video_files:
                    video_path = os.path.join(video_dir, video_files[0])
                    
                    # Copy the video to a permanent location before the temp dir is deleted
                    permanent_path = f"{tempfile.gettempdir()}/recorded_video_{os.urandom(8).hex()}.mp4"
                    shutil.copy(video_path, permanent_path)
                    
                    return permanent_path
                
                return None
    
    except Exception as e:
        print(f"Error converting HTML to video: {e}")
        return None

async def screenshotweb(
    url, 
    screenshot_path=None, 
    video_path=None, 
    record_duration=5,
    viewport_width=1920,
    viewport_height=1080,
    browser_type='chromium'
):
    """
    Advanced web capture with more configuration options
    """
    async with async_playwright() as p:
        # Select browser type
        browser_launch = {
            'chromium': p.chromium,
            'firefox': p.firefox,
            'webkit': p.webkit
        }.get(browser_type.lower(), p.chromium)
        
        # Launch browser
        browser = await browser_launch.launch()
        
        context = await browser.new_context(record_video_dir=video_path)
        page = await context.new_page()
        
        try:
            await page.goto(url, wait_until='networkidle')
            
            # Take screenshot
            if screenshot_path:
                await page.screenshot(path=screenshot_path, full_page=True)
            
            # Record video
            if video_path:
                await asyncio.sleep(record_duration)
        
        except Exception as e:
            print(f"Capture error: {e}")
        
        finally:
            await browser.close()

async def bratgenerator(text):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            await page.goto('https://www.bratgenerator.com/')
            await page.click('#toggleButtonWhite')
            await page.locator('#textInput').fill(text)
            output = f"{text}.jpg"
            await page.locator('#textOverlay').screenshot(path=output)
            return output
        except Exception as e:
            raise e
        finally:
            await browser.close()

async def scrape_bing(query, pages):
    results = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for i in range(0, pages * 10, 10):
            target_url = f"https://www.bing.com/search?q={query}&rdr=1&first={i+1}"
            tasks.append(fetch_page(session, target_url))

        responses = await asyncio.gather(*tasks)  

        for page_num, html_content in enumerate(responses):
            soup = BeautifulSoup(html_content, 'html.parser')
            completeData = soup.find_all("li", {"class": "b_algo"})

            for i, data in enumerate(completeData):
                result = {}
                result["Title"] = data.find("a").text if data.find("a") else None 
                result["link"] = data.find("a").get("href") if data.find("a") else None
                result["Description"] = data.find("div", {"class": "b_caption"}).text if data.find("div", {"class": "b_caption"}) else None
                results.append(result)

    return results

async def scrape_bing_images(query, pages):
    """Scrapes Bing images and returns a JSON list of image data."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36"
    }

    query = query.split()
    query = '+'.join(query) 
    url = f"http://www.bing.com/images/search?q={query}&FORM=HDRSC2"

    image_data = []

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url) as response:
            soup = BeautifulSoup(await response.text(), 'html.parser')
            for a in soup.find_all("a", {"class": "iusc"}):
                m = json.loads(a["m"])
                murl = m["murl"]

                image_name = urllib.parse.urlsplit(murl).path.split("/")[-1]
                image_data.append({
                    "title": image_name,
                                        "url": murl
                })

    return image_data

async def miyanBooru(query, sType):
    if sType == "rule34":
        listUrl = await Rule34().search_image(query=query)
    elif sType == "gelbooru":
        listUrl = await Gelbooru().search_image(query=query)
    elif sType == "danbooru":
        listUrl = await Danbooru().search_image(query=query)
    elif sType == "safebooru":
        listUrl = await Safebooru().search_image(query=query)
    elif sType == "paheal":
        listUrl = await Paheal().search_image(query=query)
    elif sType == "xbooru":
        listUrl = await Xbooru().search_image(query=query)
    elif sType == "tbib":
        listUrl = await Tbib().search_image(query=query)
    elif sType == "realbooru":
        listUrl = await Realbooru().search_image(query=query)
    elif sType == "lolibooru":
        listUrl = await Lolibooru().search_image(query=query)
    else:
        return
    return listUrl


async def googleSearch(query):
    url = f"https://www.googleapis.com/customsearch/v1?key={cs_apikey}&cx={cx_id}&q={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                return await response.text()
            else:
                print(f"Error fetching results: {response.status}")
                return None

async def googleSearchImages(query):
    url = f"https://www.googleapis.com/customsearch/v1?key={cs_apikey}&cx={cx_id}&searchType=image&q={query}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                json_data = await response.json()
                data = []
                items = json_data.get("items", [])
                for item in items:
                    title = item.get("title", "")
                    url = item.get("link", "")
                    data.append({"title": title, "url": url})
                return data
            else:
                print(f"Error fetching results: {response.status}")
                return []

async def blackbox(text, model, userid):
    url = "https://www.blackbox.ai/api/chat"
    if not model:
        model = "blackboxai"
    
    randomID = await randomUUID()
    
    if userid not in blackbox_history:
        blackbox_history[userid] = []
    
    blackbox_history[userid].append({
        "role": "user",
        "content": text,
        "id": randomID
    })
    
    payload = {
        "messages": blackbox_history[userid],
        "id": randomID,
        "previewToken": None,
        "userId": None,
        "codeModelMode": True,
        "agentMode": {},
        "trendingAgentMode": {},
        "isMicMode": False,
        "userSystemPrompt": None,
        "maxTokens": 1024,
        "playgroundTopP": 0.9,
        "playgroundTemperature": 0.5,
        "isChromeExt": False,
        "githubToken": "",
        "clickedAnswer2": False,
        "clickedAnswer3": False,
        "clickedForceWebSearch": True,
        "visitFromDelta": False,
        "mobileClient": False,
        "userSelectedModel": f"{model}",
        "validated": "00f37b34-a166-4efb-bce5-1312d87f2f94"
    }
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 11; Infinix X6511B Build/RP1A.201005.001) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.39 Mobile Safari/537.36",
        'sec-ch-ua-platform': "\"Android\"",
        'sec-ch-ua': "\"Android WebView\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        'sec-ch-ua-mobile': "?1",
        'origin': "https://www.blackbox.ai",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://www.blackbox.ai/",
        'accept-language': "en,en-US;q=0.9",
        'priority': "u=1, i"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json.dumps(payload), headers=headers) as response:
            content = await response.text()
            
            blackbox_history[userid].append({
                "role": "system",
                "content": content,
                "id": randomID
            })
                            
            return content


async def tiktokData(url):
    tikwm_url = "https://www.tikwm.com/api/"
    payload = f"url={url}&hd=1"
    headers = {'Content-Type': "application/x-www-form-urlencoded"}
    async with aiohttp.ClientSession() as session:
        async with session.post(tikwm_url, data=payload, headers=headers) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    return data['data']
                except (json.JSONDecodeError, KeyError):
                    return json.dumps({"code": -1, "msg": "Error parsing response"})
            else:
                return json.dumps({"code": -1, "msg": "Error fetching data from TikTok"})

async def tiktokDataFromUser(username):
    tikwm_url = "https://www.tikwm.com/api/user/posts"
    payload = f"unique_id={username}&hd=1"
    headers = {'Content-Type': "application/x-www-form-urlencoded"}
    async with aiohttp.ClientSession() as session:
        async with session.post(tikwm_url, data=payload, headers=headers) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    return data['data']
                except (json.JSONDecodeError, KeyError):
                    return json.dumps({"code": -1, "msg": "Error parsing response"})
            else:
                return json.dumps({"code": -1, "msg": "Error fetching data from TikTok"})

async def tiktokSearch(keywords):
    url = "https://www.tikwm.com/api/feed/search"
    payload = f"keywords={keywords}&hd=1"
    headers = {'Content-Type': "application/x-www-form-urlencoded"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    return data['data']
                except (json.JSONDecodeError, KeyError):
                    return json.dumps({"code": -1, "msg": "Error parsing response"})
            else:
                return json.dumps({"code": -1, "msg": "Error fetching data from TikTok"})

async def tiktokSearchImage(keywords):
    url = "https://www.tikwm.com/api/photo/search"
    payload = f"keywords={keywords}&hd=1"
    headers = {'Content-Type': "application/x-www-form-urlencoded"}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload, headers=headers) as response:
            if response.status == 200:
                try:
                    data = await response.json()
                    return data['data']
                except (json.JSONDecodeError, KeyError):
                    return json.dumps({"code": -1, "msg": "Error parsing response"})
            else:
                return json.dumps({"code": -1, "msg": "Error fetching data from TikTok"})

async def fetch_pixiv_illusts(query):
    url = "https://www.pixiv.net/touch/ajax/search/illusts"
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
        'Accept': "application/json",
        'Accept-Encoding': "gzip, deflate",
        'x-user-id': "94263110",  
        'x-requested-with': "mark.via.gp",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'accept-language': "en-US,en;q=0.9"
    }
    
    params = {
        'include_meta': "1",
        's_mode': "s_tag",
        'type': "all",
        'word': query,
        'csw': "0",
        'lang': "en",
        'version': "08a9c37ead5e5b84906f6cbcdb92429ae5d13ac8"  
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            response.raise_for_status()  
            data = await response.json()
            sifat = data['body']['illusts']
            return sifat

async def fetch_pixivnsfw_illusts(query):
    url = "https://www.pixiv.net/touch/ajax/search/illusts"
    
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.91 Mobile Safari/537.36",
        'Accept': "application/json",
        'Accept-Encoding': "gzip, deflate",
        'x-user-id': "94263110",  
        'x-requested-with': "mark.via.gp",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'accept-language': "en-US,en;q=0.9",
        'Cookie': "first_visit_datetime=2024-04-03%2004%3A40%3A06; webp_available=1; cc1=2024-04-03%2004%3A40%3A06; __cf_bm=bFgcDe3ii0g4jGx2F3DaTDiqI45tTIjmVirfgKzgTA4-1712086806-1.0.1.1-PmaKCsuVW2_qPpzumrNho6ncdxvJbWvzelbYkqw0GT5cwcVnzPFr0qlfKc7hBR6M8RfL93yA8hcxjHuyGgOwCPtaXw.WiW7v1bE_EoD9qa8; p_ab_id=4; p_ab_id_2=4; p_ab_d_id=2029578662; __utma=235335808.2120078818.1712086808.1712086808.1712086808.1; __utmc=235335808; __utmz=235335808.1712086808.1.1.utmcsr=pixiv.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmt=1; yuid_b=hCloOQA; _lr_geo_location_state=JB; _lr_geo_location=ID; _fbp=fb.1.1712086811148.1166980283; privacy_policy_agreement=6; _gid=GA1.2.910677620.1712086814; _ga_MZ1NL4PHH0=GS1.1.1712086816.1.0.1712086819.0.0.0; PHPSESSID=94263110_Fw0KsX7pznqpdYz3lK8R9yh9XYu50q0o; device_token=716919cff64a5320628cdf79ef4516b7; c_type=21; privacy_policy_notification=0; a_type=0; b_type=0; __utmv=235335808.|2=login%20ever=yes=1^3=plan=normal=1^6=userid=94263110=1^9=p_ab_id=4=1^10=p_ab_id_2=4=1^11=lang=en=1^20=webp_available=yes=1; FCNEC=%5B%5B%22AKsRol-vCV9Hxuv0y5QgiXeC7T-BFYOrFVWJvquAW_a5dNJiomRpbw066zUVZyChY-7_loUKPrge1Xgfo4sIaFNaT5QLn_P22E2gS5ixUk2rUaobfhHC_pIaUYonV7bEpHq41Veo260DpW-4UuhCLkY4qTNun5Wopw%3D%3D%22%5D%5D; QSI_S_ZN_5hF4My7Ad6VNNAi=v:0:0; AMZN-Token=v2FweIBDV2dteXFXRmk0S2gzYlJ4WFFqZldkbTJrTkZ4WmVMTFNjMkV3RTRjNkdreWV1OGJscVpVQmhNcmVtVjlKamlISkIyK1QxcWV3a2gxM3lTZ0FWT3huQ21sWG0vTUlqRE9EbUg3bEErMmRJeWF5SXRySm16R2dYbVFpV1RPQ05vZGJrdgFiaXZ4HFNlKy92VWp2djcwMTc3KzlZeHQrNzcrOWRBQT3/; _pbjs_userid_consent_data=3524755945110770; _pubcid=4aecfda8-5100-45c7-9836-613f14880002; __gads=ID=a6eeb3b4c0a14363:T=1712086878:RT=1712086878:S=ALNI_MYl268T5t3l4KpQWHzo5sdDEn5fzQ; __eoi=ID=a5a1aef87f689702:T=1712086878:RT=1712086878:S=AA-AfjY3vOosEQzzth1nrPh5ZE5t; _im_vid=01HTG5941DFM57X0VR5XJ0HD20; cto_bundle=I5qpx19idyUyQnhKMHhYQnpLYjRqRWZQYXglMkZRYWNnY1V4WTdxOFpUTU5xd3c4c0p6M3FJRFYwZHVJSGIxNmFFc3ZoTWtmckNpTjJnb0lIUkRpajB1cWNMS3VocjNxWHdKZ3hKRWNuNzcyeGJKT3B2UkdKUHhLbGpCZGlycFF6UDhpWjBVOXlKRmpkODZZOSUyQmRSYTBuN2hXTk9QYkElM0QlM0Q; cto_bidid=hHBLll94dnBBd3pBRG0yJTJCT0dHNlJxMnB3SVUwMnY0UG1ESVRSeTdMQTVUT0xYQ29CaGdGdjFQdThVYVRqYnhrS3IzaWJzR2Vpb0FkWEowVzNxdlBUWXFydyUyQjlwbGhUaHlkUm5HaW9nOTNWJTJCUGc0ayUzRA; MgidStorage=%7B%220%22%3A%7B%22svspr%22%3A%22%22%2C%22svsds%22%3A1%7D%2C%22C1298385%22%3A%7B%22page%22%3A1%2C%22time%22%3A%221712086885038%22%7D%2C%22C1298391%22%3A%7B%22page%22%3A1%2C%22time%22%3A%221712086885023%22%7D%7D; __utmb=235335808.8.9.1712086837707; _ga_3WKBFJLFCP=GS1.1.1712086807.1.1.1712087230.0.0.0; _ga=GA1.1.2120078818.1712086808"
    }
    
    params = {
        'include_meta': "1",
        's_mode': "s_tag",
        'type': "all",
        'word': query,
        'csw': "0",
        'lang': "en",
        'version': "08a9c37ead5e5b84906f6cbcdb92429ae5d13ac8"  
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, headers=headers) as response:
            response.raise_for_status()  
            data = await response.json()
            sifat = data['body']['illusts']
            return sifat


# Route
@app.route('/blackbox')
async def process_blackbox():
    try:
        text = request.args.get('text')
        userid = request.args.get('userid') or "Miyan"
        model = request.args.get('model') or "blackboxai"
        if not text:
            return jsonify({'error': 'Missing text parameter'}), 400
        response = await blackbox(text, model, userid)
        history = blackbox_history.get(userid, [])
        if model == "blackboxai":
            content = "\n".join(response.splitlines()[4:])
        else:
            content = response
        return jsonify({'creator': '@Miyan', 'result': content, 'history_length': len(history)}), 200
    except requests.RequestException as e:
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except (IndexError, KeyError) as e:
        return jsonify({'error': f'Failed to process response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/ai')
@app.route('/gemini')
async def process_ai():
    file_url = request.args.get('file_url')
    model = request.args.get('model') or gemini_default_model
    text = request.args.get('text')
    realtime = request.args.get('realtime') or False
    userid = request.args.get('userid')
    prompt = request.args.get('prompt')
    url_pattern = r'(https?://[^\s]+(?:\?[^\s]*)?)'
    urls = re.findall(url_pattern, text)

    try:
        if not text:
            return jsonify({'error': 'Missing text parameter'}), 400

        
        if urls:
            async with aiohttp.ClientSession() as session:
                async with session.get(urls[0], allow_redirects=True) as web_response:
                    web_content = await web_response.text()
                    text = f'{web_content}\n\n{text}'

        
        if userid:
            if userid not in ai_history:
                ai_history[userid] = []
            
            
            ai_history[userid].append({
                "role": "user",
                "parts": [text]
            })

        
        if prompt:
            model = genai.GenerativeModel(
                model_name=f"{model}",
                system_instruction=f"{prompt}",
                safety_settings={
                    genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                    genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                    genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                }
            )
        else:
            model = genai.GenerativeModel(
                model_name=f"{model}",
                safety_settings={
                    genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH: genai.types.HarmBlockThreshold.BLOCK_NONE,
                    genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                    genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: genai.types.HarmBlockThreshold.BLOCK_NONE,
                }
            )

        
        chat = model.start_chat(
            history=ai_history[userid] if userid and ai_history.get(userid) else None
        )

        
        if realtime:
            google_search_result = await googleSearch(text)
            if google_search_result:
                response = chat.send_message([google_search_result, '\n\n', text])
            else:
                return jsonify({'error': 'Failed to fetch Google Search results'}), 500
        elif file_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(file_url) as response:
                    filename = os.path.basename(file_url)
                    with open(filename, 'wb') as gm:
                        gm.write(await response.read())
                    files = [await upload_to_gemini(filename)]
                    await wait_for_files_active(files)
            response = chat.send_message([files[0], '\n\n', text])
        else:
            response = chat.send_message(text)

        
        if userid:
            ai_history[userid].append({
                "role": "model",
                "parts": [response.text]
            })

        return jsonify({
            'status': 200,
            'creator': '@Miyan',
            'result': response.text,
            'history_length': len(ai_history[userid]) if userid in ai_history else 0
        }), 200

    except Exception as e:
        print(f"Error processing request: {str(e)}")  
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/aihistory')
async def get_aihistory():
    userid = request.args.get('userid')
    if not userid:
        return jsonify({'error': 'Missing userid parameter'}), 400
    
    history = ai_history.get(userid, [])
    return jsonify({
        'status': 200,
        'history': history,
        'history_length': len(history)
    })

@app.route('/blackboxhistory')
async def get_blackboxhistory():
    userid = request.args.get('userid')
    if not userid:
        return jsonify({'error': 'Missing userid parameter'}), 400
    
    history = blackbox_history.get(userid, [])
    return jsonify({
        'status': 200,
        'history': history,
        'history_length': len(history)
    })

@app.route('/googleImages')
async def process_googleimages():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    try:
        data = await googleSearchImages(query)  
        return jsonify({'creator': '@Miyan', 'data': data}), 200
    except requests.RequestException as e:
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except (IndexError, KeyError) as e:
        return jsonify({'error': f'Failed to process response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
        
@app.route('/googleSearch')
async def process_googlesearch():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    try:
        data = await googleSearch(query) 
        return jsonify({'creator': '@Miyan', 'data': data}), 200
    except requests.RequestException as e:
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except (IndexError, KeyError) as e:
        return jsonify({'error': f'Failed to process response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/booru')
async def process_booru():
    query = request.args.get('query')
    nsfwType = request.args.get('type') or "rule34"
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    try:
        listUrl = await miyanBooru(query, nsfwType) 
        return jsonify({'creator': '@Miyan', 'url': listUrl}), 200
    except requests.RequestException as e:
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except (IndexError, KeyError) as e:
        return jsonify({'error': f'Failed to process response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/bingSearch')
async def process_bingsearch():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    try:
        data = await scrape_bing(query=query, pages=10) 
        return jsonify({'creator': '@Miyan', 'data': data}), 200
    except requests.RequestException as e:
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except (IndexError, KeyError) as e:
        return jsonify({'error': f'Failed to process response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/bingImages')
async def process_bingimages():
    query = request.args.get('query')
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    try:
        data = await scrape_bing_images(query=query, pages=10) 
        return jsonify({'creator': '@Miyan', 'data': data}), 200
    except requests.RequestException as e:
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except (IndexError, KeyError) as e:
        return jsonify({'error': f'Failed to process response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

        
@app.route('/pixiv')
async def process_pixiv():
    query = request.args.get('query') 
    nsfw = request.args.get('nsfw') 
    if not query:
        return jsonify({'error': 'Missing query parameter'}), 400
    try:
        if not nsfw:
            pixivdata = await fetch_pixiv_illusts(query)
        elif nsfw:
            pixivdata = await fetch_pixivnsfw_illusts(query)
        return jsonify({'creator': '@Miyan', 'data': pixivdata}), 200

    except requests.RequestException as e:
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except (IndexError, KeyError) as e:
        return jsonify({'error': f'Failed to process response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500


@app.route('/yt')
@app.route('/youtube')
async def process_youtube():
    query = request.args.get('query')
    url = request.args.get('url')
    try:
        if query:
            results = Search(query).results
            data = []
            for video in results:
                data.append({
                    'title': video.title,
                    'url': video.watch_url,
                    'length': video.length,
                    'views': video.views,
                    'thumbnail': video.thumbnail_url,
                    'description': video.description
                })
            return jsonify({'creator': '@Miyan', 'data': data}), 200
        
        if url:
            yt = YouTube(url, on_progress_callback=on_progress)
            vid = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            aud = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
            video_info = {
                'title': yt.title,
                'url': yt.watch_url,
                'video_url': await tourl(vid.download()),
                'audio_url': await tourl(aud.download()),
                'length': yt.length,
                'views': yt.views,
                'thumbnail': yt.thumbnail_url,
                'description': yt.description,
                'author': yt.author,
                'publish_date': yt.publish_date.strftime('%Y-%m-%d') if yt.publish_date else None,
            }
            return jsonify({'creator': '@Miyan', 'data': video_info}), 200
        
        if not query and not url:
            return jsonify({'error': 'Need 1 Parameter, But 2 Was Given'}), 400
    
    except requests.RequestException as e:
        return jsonify({'error': f'API request failed: {str(e)}'}), 500
    except (IndexError, KeyError) as e:
        return jsonify({'error': f'Failed to process response: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500
        
        
       
@app.route('/ytDownload')
@app.route('/youtubeDownload')
async def youtubeDownload():
    url = request.args.get('url')
    download_type = request.args.get('type', 'video')
    
    if not url:
        return jsonify({'error': 'URL parameter is required'}), 400
    
    try:
        yt = YouTube(url, on_progress_callback=on_progress)
        
        if download_type == 'video':
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        elif download_type == 'audio':
            stream = yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
        else:
            return jsonify({'error': 'Invalid type parameter. Use "audio" or "video"'}), 400
        
        if not stream:
            return jsonify({'error': 'No suitable stream found for download'}), 404
        
        return await send_file(stream.download(), as_attachment=True), 200

    except Exception as e:
        return jsonify({'error': f'Failed to download or upload: {str(e)}'}), 500
       
@app.route('/brat')
async def process_brat():
    text = request.args.get('text')
    
    if not text:
        return jsonify({'error': 'text parameter is required'}), 400
    
    try:
        output = await bratgenerator(text)
        return await send_file(output, as_attachment=True), 200

    except Exception as e:
        return jsonify({'error': f'Failed to download or upload: {str(e)}'}), 500

@app.route('/htmltoimage')
async def process_htmltoimage():
    text = request.args.get('text')
    
    if not text:
        return jsonify({'error': 'text parameter is required'}), 400
    
    try:
        output = await html_to_image(text)
        return await send_file(output, as_attachment=True), 200

    except Exception as e:
        return jsonify({'error': f'Failed to download or upload: {str(e)}'}), 500

@app.route('/htmltovideo')
async def process_htmltovideo():
    text = request.args.get('text')
    
    if not text:
        return jsonify({'error': 'text parameter is required'}), 400
    
    try:
        output = await html_to_video(text)
        return await send_file(output, as_attachment=True), 200

    except Exception as e:
        return jsonify({'error': f'Failed to download or upload: {str(e)}'}), 500

@app.route('/screenshotweb')
@app.route('/ssweb')
async def process_ssweb():
    url = request.args.get('url')
    sstype = "image"
    
    if not url:
        return jsonify({'error': 'url parameter is required'}), 400
    
    try:
        if sstype == "image":
            path = await randomUUID() + ".jpg"
            await screenshotweb(
            url, 
            screenshot_path=path,
            browser_type='chromium'
        )
            return await send_file(path, as_attachment=True), 200
        if sstype == "video":
            path = await randomUUID() + ".mp4"
            await screenshotweb(
            url, 
            video_path=path,
            record_duration=5,
            browser_type='chromium'
        )
            return await send_file(path, as_attachment=True), 200

    except Exception as e:
        return jsonify({'error': f'Failed to download or upload: {str(e)}'}), 500
       

@app.route('/tt')
@app.route('/tiktok')
async def process_tiktok():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'url parameter is required'}), 400
    results = await tiktokData(url)
    if results:
        return jsonify({'creator': '@Miyan', 'data': results}), 200
    else:
        return jsonify({'error': 'No similar images found or an error occurred.'}), 500

@app.route('/ttUser')
@app.route('/tiktokUser')
async def process_tiktokuser():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'username parameter is required'}), 400
    results = await tiktokDataFromUser(username)
    if results:
        return jsonify({'data': results}), 200
    else:
        return jsonify({'error': 'No similar images found or an error occurred.'}), 500

@app.route('/ttSearch')
@app.route('/tiktokSearch')
async def process_tiktoksearch():
    query = request.args.get('query')
    searchType = request.args.get('searchType')
    if not query:
        return jsonify({'error': 'query parameter is required'}), 400

    if not searchType or searchType == "video":
        results = await tiktokSearch(query) 
    elif searchType == "image":
        results = await tiktokSearchImage(query) 
    
    if results:
        return jsonify({'creator': '@Miyan', 'data': results}), 200
    else:
        return jsonify({'error': 'No data found or an error occurred.'}), 500


@app.route('/deleteallsession')
async def delete_all_session():
    key = request.args.get('key')
    if key != 'Miyan1EFF2FE1':
        return jsonify({'error': 'Unauthorized access'}), 403
    try:
        ai_history.clear()
        blackbox_history.clear()
        return jsonify({'message': 'All sessions deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': f'Failed to delete sessions: {str(e)}'}), 500

@app.route('/')
@app.route('/home')
async def process_home():
    return await render_template('hello_world.html')

@app.errorhandler(Exception)
async def handle_all_errors(error):
    status_code = getattr(error, 'code', 500)
    return jsonify({
        "creator": "@Miyan",
        "error": error.description if hasattr(error, 'description') else "An unexpected error occurred"
    }), status_code

if __name__ == '__main__':
    config = Config()
    config.bind = ["0.0.0.0:5000"]  # Atur host dan port sesuai kebutuhan
    asyncio.run(hypercorn.asyncio.serve(app, config))