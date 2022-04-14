from PIL import Image
import requests


def get_size_of_img(url):
    r = requests.get(url, stream=True)
    if not r.ok:
        return None
    image = Image.open(r.raw)
    return image.size


def zoom_ratio(width, height, max_width=None, max_height=None):
    ratio = 100
    if max_width and width > max_width:
        ratio = int((max_width / width) * 100)

    if max_height and height > max_height:
        r = int((max_height / height) * 100)
        ratio = min(r, ratio)
    return ratio


def calc_zoom_ratio(url, max_width=None, max_height=None):
    size = get_size_of_img(url)
    if size is None:
        return 100

    width, height = size
    return zoom_ratio(width, height, max_width, max_height)
