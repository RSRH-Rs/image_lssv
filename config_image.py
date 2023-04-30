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
    col_num = 1 # 列数
    total = len(sv_list)
    
    # 长宽比最小25%，若比例过怪，则分多列展示
    _width, _height = width, height
    while _width / _height <= 0.25:
        col_num += 1
        _width = width * col_num + 26 * (col_num - 1)
        # 高度取配置需要的和第一列需要的max
        col_lines = math.ceil((total + 5) / col_num)
        _height = max(col_lines * 155, (col_lines - 5) * 155 + 850)  
            
    size = (_width, _height)
    resized_image = crop_center_img(image,based_w=size[0],based_h=size[1])
    
    for index, key in enumerate(sv_list):
        tasks.append(_draw_config_line(resized_image, key, index, sv_list[key], total, col_num))

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


async def _draw_config_line(img: Image.Image, sv_name: str, index: int, status: bool, total: int, col_num :int = 1):
    config_line = Image.open(get_path("data", "imgs", "line.png"))
    config_line_draw = ImageDraw.Draw(config_line)
    config_line_draw.text((52, 65), sv_name, first_color, gs_font_36, 'lm')
    if status:
        config_line.paste(config_on, (613, 21), config_on)
    else:
        config_line.paste(config_off, (613, 21), config_off)
    
    if col_num == 1:
        img.paste(config_line, (26, 850 + index * 155), config_line)
    else:
        col_lines = math.ceil((total + 5) / col_num) # 每列最大条数，第二列开始不需要lssv_title，多出5条的位置
        if index + 5 < col_lines:
            img.paste(config_line, (26, 850 + index * 155), config_line)
        else:
            col_current = (index + 5) // col_lines # 当前列
            index = index + 5 - col_lines * col_current
            img.paste(config_line, (
                26 * col_current + 850 * col_current,
                index * 155 
            ), config_line)

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

