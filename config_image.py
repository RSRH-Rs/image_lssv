from .utils import get_path,get_random_pic
from PIL import Image,ImageFont,ImageDraw
import asyncio
import math
from .fonts import gs_font_27,gs_font_40,gs_font_36
import json
import requests
from io import BytesIO
from pathlib import Path
from base64 import b64encode
from typing import Union, overload
from PIL import Image, ImageFont
from nonebot import CommandSession
import json

first_color = (20, 20, 20)
second_color = (57, 57, 57)

images_path = get_path("data","imgs")
config_on = Image.open(get_path(images_path,"config_on.png"))
config_off = Image.open(get_path(images_path,"config_off.png"))



async def get_image_services(sv_list:dict,image:Image,group_id:str,width:int,height:int) -> Image:
    tasks = []
    size = (width, height)

    resized_image = crop_center_img(image,based_w=size[0],based_h=size[1])
    for index, key in enumerate(sv_list):
        tasks.append(_draw_config_line(resized_image, key, index, sv_list[key]))

    tasks_ = asyncio.gather(*tasks)


    sv_title = Image.open(get_path("data","imgs","lssv_title.png"))
    resized_image.paste(sv_title,(0,0),sv_title)

    img_draw = ImageDraw.Draw(resized_image)
    on_count, off_count = sum(sv_list.values()), len(sv_list) - sum(sv_list.values())
    img_draw.text((383, 467), str(group_id), first_color, gs_font_27, 'mm')
    img_draw.text((185, 600), str(len(sv_list)), first_color, gs_font_40, 'mm')
    img_draw.text((431, 600), str(on_count), first_color, gs_font_40, 'mm')
    img_draw.text((680, 600), str(off_count), first_color, gs_font_40, 'mm')

    await tasks_
    return resized_image


async def _draw_config_line(img: Image.Image, sv_name: str, index: int, status:bool):
    config_line = Image.open(get_path("data", "imgs", "line.png"))
    config_line_draw = ImageDraw.Draw(config_line)
    config_line_draw.text((52, 65), sv_name, first_color, gs_font_36, 'lm')
    if status:
        config_line.paste(config_on, (613, 21), config_on)
    else:
        config_line.paste(config_off, (613, 21), config_off)

    img.paste(config_line, (26, 850 + index * 155), config_line)

def crop_center_img(
    img: Image.Image, based_w: int, based_h: int
) -> Image.Image:
    # 确定图片的长宽
    based_scale = '%.3f' % (based_w / based_h)
    w, h = img.size
    scale_f = '%.3f' % (w / h)
    new_w = math.ceil(based_h * float(scale_f))
    new_h = math.ceil(based_w / float(scale_f))
    if scale_f > based_scale:
        resize_img = img.resize((new_w, based_h), Image.ANTIALIAS)
        x1 = int(new_w / 2 - based_w / 2)
        y1 = 0
        x2 = int(new_w / 2 + based_w / 2)
        y2 = based_h
    else:
        resize_img = img.resize((based_w, new_h), Image.ANTIALIAS)
        x1 = 0
        y1 = int(new_h / 2 - based_h / 2)
        x2 = based_w
        y2 = int(new_h / 2 + based_h / 2)
    crop_img = resize_img.crop((x1, y1, x2, y2))
    return crop_img


#

