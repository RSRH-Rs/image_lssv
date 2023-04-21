import asyncio
import requests
import json
import re
import datetime
import os
from PIL import Image


SENTENCES_API = "https://v1.hitokoto.cn/"
RANDOM_PIC_API = "https://www.loliapi.com/acg/pe/"

date_in_Chinese = {
    "Monday":"星期一",
    "Tuesday":"星期二",
    "Wednesday":"星期三",
    "Thursday":"星期四",
    "Friday":"星期五",
    "Saturday":"星期六",
    "Sunday":"星期天",
}

def get_date():
    today = datetime.datetime.today()
    year = today.year
    month = today.month
    day = today.day
    day_of_week = today.strftime("%A")

    return {
        "Chinese":date_in_Chinese[day_of_week],
        "English":day_of_week,
        "year":year,
        "month":month,
        "day":day,
    }


def get_path(*paths) -> str:
    return os.path.join(os.path.dirname(__file__), *paths)

def get_sentence(format:bool=True):
    response = requests.get(url=SENTENCES_API)
    data = json.loads(response.text)
    sentence = {
        "content":data["hitokoto"],
        "from":data["from"],
        "from_who":(data["from_who"] if data["from_who"] else data['creator']) if data["from"] != data['from_who'] and data['creator'] != data['from_who'] else ""
    }
    if format:
        return re.sub(".*?《.*?》.*?",f"",sentence['content']) + f"《{sentence['from']}》" + f" - {sentence['from_who']} " if sentence['from_who'] else ""

def get_random_pic(file_name:str) -> Image:
    response = requests.get(url=RANDOM_PIC_API)
    content = response.content
    save_path = get_path("data", "imgs", file_name)
    with open(save_path, mode="wb") as f:
        f.write(content)
    return Image.open(save_path)

def get_json_data(file_path) -> dict:
    with open(file_path,mode="r") as f:
        try:
            return json.loads(f.read())
        except json.decoder.JSONDecodeError:
            return {}

def write_json_data(file_path,content:dict,mode:str="append"):
    with open(file_path,mode="r+") as f:
        if mode == "append":
            data:dict = json.loads(f.read())
            data.update(content)
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()
        else:
            f.seek(0)
            f.write(json.dumps(content))
            f.truncate()




