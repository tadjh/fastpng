"""
    Main module for the FastPNG application
"""

from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel

import io
import time
import math
import base64
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

class ImageRequest(BaseModel):
    font: str
    text: str
    fontColor: str = "FFFFFF"
    fontSize: int= 40
    width: int = 512
    height: int = 512
    offsetX: int = 256
    offsetY: int = 256
   
@app.post("/generate-image", responses={200: {"content": {"image/png": {}}}})
async def generate_image(imageRequest: ImageRequest):
    """Generates an image with the given text and font

    Args:
        class ImageRequest {
            font (str): The font name from /fonts
            text (str): The text to be displayed
            fontColor (str, optional): Color of font in HEX. Defaults to "FFFFFF" (White).
            fontSize (int, optional): The font size in pixels. Defaults to 40.
            width (int, optional): The Image width in pixels. Defaults to 512.
            height (int, optional): The Image height in pixels. Defaults to 512.
            offsetX (int, optional): The position in pixels the anchor will offset from along the x-axis. Defaults to 256.
            offsetY (int, optional): The position in pixels the anchor will offset from along the y-axis. Defaults to 256.
        }

    Returns:
        File: The generated PNG file
    """    
    if imageRequest.font not in font_mapping:
        return {"error": "Font not found"}
    
    sanitized_font_colour = imageRequest.fontColor.lstrip("#")

    # check that font_colour is a valid hex code
    if not all(c in "0123456789ABCDEF" for c in sanitized_font_colour):
        return {"error": "Invalid font colour"}

    start_time = time.time()

    image = Image.new("RGBA", (imageRequest.width, imageRequest.height), (0, 0, 0, 0))

    # logger.debug(f"Font: {imageRequest.font}, Text: {imageRequest.text}")
    optimal_font_size = imageRequest.fontSize

    font_file = ImageFont.truetype(font_mapping[imageRequest.font], optimal_font_size)

    text_length = font_file.getlength(imageRequest.text)
    
    ratio = imageRequest.width * 0.97 / text_length

    if ratio < 1:
        optimal_font_size = math.floor(optimal_font_size * ratio)    
    
    # logger.debug(f"Text Length: {textLength}, Ratio: {ratio}, Font Size: {imageRequest.font_size}")

    font_file = ImageFont.truetype(font_mapping[imageRequest.font], optimal_font_size)

    # convert font_colour hex code to tuple
    font_colour_tuple = tuple(int(sanitized_font_colour[i:i+2], 16) for i in (0, 2, 4))

    draw = ImageDraw.Draw(image)

    draw.text((imageRequest.offsetX, imageRequest.offsetY), imageRequest.text, font=font_file, fill=font_colour_tuple, anchor="mm")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    # bytes
    result = buffer.getvalue()

    # Base 64 Alternative
    # buffer.seek(0)
    # result = "data:image/png;base64," + base64.b64encode(buffer.getvalue()).decode()

    end_time = time.time()
    logger.info(f"Time taken: {end_time - start_time} seconds")

    return Response(
        result,
        media_type="image/png",
        headers={
            "x-time-taken": f"{end_time-start_time}",
            "x-image-size": f"{imageRequest.width}x{imageRequest.height}",
            "x-font-size": f"{optimal_font_size}",
        },
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
