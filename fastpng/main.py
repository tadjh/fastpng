"""
    Main module for the FastPNG application
"""

from fastapi import FastAPI
from fastapi.responses import Response


import io
import time
import math
from PIL import Image, ImageDraw, ImageFont
from matplotlib import font_manager

from .settings import Settings

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


config = Settings()

logger.debug(config.redis_dsn)
logger.debug(type(config.redis_dsn))


app = FastAPI()
"""
    Application object for the FastPNG application
"""

# font mapping
all_fonts = font_manager.fontManager.ttflist
font_mapping = {}
for font in all_fonts:
    font_mapping[font.name] = font.fname
all_fonts = None


@app.get("/")
def read_root():
    """Root endpoint

    Returns:
        Hello: World
    """
    return {"Hello": "World"}


@app.get("/health")
def health_check():
    """Health Check endpoint

    Returns:
        status: ok
    """
    return {"status": "ok"}


@app.get("/fonts")
def read_fonts():
    """Returns the list of available font names

    Returns:
        list: Font Names
    """
    # font_keys = list(font_mapping.keys())
    # sorted_font_keys = sorted(font_keys)
    # return sorted_font_keys
    return sorted(list(font_mapping.keys()))


@app.get("/generate_image", responses={200: {"content": {"image/png": {}}}})
async def generate_image(font: str, text: str, font_colour: str= "FFFFFF"):
    """Generates an image with the given text and font

    Args:
        font (str): The font name from /fonts
        text (str): The text to be displayed
        font_colour (str, optional): Colour of font in HEX. Defaults to "FFFFFF" (White).

    Returns:
        File: The generated PNG file
    """    
    if font not in font_mapping:
        return {"error": "Font not found"}

    start_time = time.time()
    image = Image.new("RGBA", (512, 256), (255, 255, 255, 255))
    font_size = 16
    logger.debug(f"Font: {font}, Text: {text}")
    font_file = ImageFont.truetype(font_mapping[font], font_size)

    # Holy Fuck this was a bad idea to scale it in this method
    # logger.debug(f"Font bounding box: {font_file.getbbox(text)}, Image Size: {image.size}, Mathed: {image.size[0] * (font_pct / 100)}")
    # while font_file.getbbox(text)[0] < image.size[0] * (font_pct / 100):
    #     font_size += 1
    #     font_file = ImageFont.truetype(font_mapping[font], font_size)
    #     logger.debug(f"Font Size: {font_size}")

    # scales font size to image size
    textLength = font_file.getlength(text) # gets length of text in pixels at size of 16
    ratio = 500 / textLength # ratio is fixed width of 500 divided by the pixel length
    if ratio < 1:
        font_size = math.floor(font_size * (1 + ratio))
    elif ratio > 1:
        font_size = math.floor(font_size * ratio)
    
    logger.debug(f"Text Length: {textLength}, Ratio: {ratio}, Font Size: {font_size}")

    font_file = ImageFont.truetype(font_mapping[font], font_size)

    # convert font_colour hex code to tuple
    font_colour = font_colour.lstrip("#")
    font_colour_tuple = tuple(int(font_colour[i:i+2], 16) for i in (0, 2, 4))

    draw = ImageDraw.Draw(image)
    image_size = image.size
    draw.text((image_size[0]/2, image_size[1]/2), text, font=font_file, fill=font_colour_tuple, anchor="mm")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    end_time = time.time()
    logger.info(f"Time taken: {end_time - start_time} seconds")

    
    return Response(
        buffer.getvalue(),
        media_type="image/png",
        headers={
            "x-image-size": f"{image_size[1]}x{image_size[0]}",
            "x-time-taken": f"{end_time-start_time}",
            "x-font-size": f"{font_size}",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
