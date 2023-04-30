import requests
import json
import os
from PIL import Image
from typing import Optional, Tuple
import httpx
from aiohttp.client import ClientSession
from io import BytesIO

RANDOM_PIC_API = "https://www.loliapi.com/acg/pe/"
def get_path(*paths) -> str:
    return os.path.join(os.path.dirname(__file__), *paths)


async def get_random_pic(file_name: str) -> Image.Image:
    save_path = get_path("data", "imgs", file_name)
    async with ClientSession() as session:
        async with session.get(url=RANDOM_PIC_API) as response:
            content = await response.content.read()
            with open(save_path,mode="wb") as f:
                f.write(content)
            return Image.open(save_path)


def get_json_data(file_path) -> dict:
    with open(file_path, mode="r") as f:
        try:
            return json.loads(f.read())
        except json.decoder.JSONDecodeError:
            return {}


def write_json_data(file_path, content: dict, mode: str = "append"):
    with open(file_path, mode="r+") as f:
        if mode == "append":
            data: dict = json.loads(f.read())
            data.update(content)
            f.seek(0)
            f.write(json.dumps(data))
            f.truncate()
        else:
            f.seek(0)
            f.write(json.dumps(content))
            f.truncate()


async def get_pic(url, size: Optional[Tuple[int, int]] = None) -> Image.Image:
    """
    从网络获取图片, 格式化为RGBA格式的指定尺寸
    """
    async with httpx.AsyncClient(timeout=None) as client:
        resp = await client.get(url=url)
        if resp.status_code != 200:
            if size is None:
                size = (960, 600)
            return Image.new("RGBA", size)
        pic = Image.open(BytesIO(resp.read()))
        pic = pic.convert("RGBA")
        if size is not None:
            pic = pic.resize(size, Image.LANCZOS)
        return pic
