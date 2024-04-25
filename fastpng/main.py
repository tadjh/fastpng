"""
    Main module for the FastPNG application
"""
from fastapi import FastAPI
from fastapi.responses import Response
from contextlib import asynccontextmanager

from fastapi_cache import FastAPICache, coder
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

from redis import asyncio as aioredis

import io
from PIL import Image, ImageDraw, ImageFont
from matplotlib import font_manager

from .settings import Settings

import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


config = Settings()

logger.debug(config.redis_dsn)
logger.debug(type(config.redis_dsn))

# application lifecycle
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     redis = await aioredis.from_url(config.redis_dsn.unicode_string())
#     FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
#     yield
#     await redis.close()


app = FastAPI(
    # lifespan=lifespan # disabled as caching within the application is disabled
    )
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
# @cache(expire=3600)
def read_fonts():
    """Returns the list of available font names

    Returns:
        list: Font Names
    """
    # font_keys = list(font_mapping.keys())
    # sorted_font_keys = sorted(font_keys)
    # return sorted_font_keys
    return sorted(list(font_mapping.keys()))


@app.get("/generate_image")
# @cache(expire=3600) #being handled by the web server proxying this application
async def generate_image(font: str, font_size: int, text: str):
    """Generates an image with the given font, font size and text

    Args:
        font (str): The font name from the list of available fonts (See /fonts endpoint)
        font_size (int): The font size of the text
        text (str): The text to be rendered

    Returns:
        File: The generated image as a PNG file
    """
    if font not in font_mapping:
        return {"error": "Font not found"}

    image = Image.new("RGBA", (512, 256), (255, 255, 255, 0))
    logger.debug(f"Font: {font}, Font Size: {font_size}, Text: {text}")
    font_file = ImageFont.truetype(font_mapping[font], font_size)

    draw = ImageDraw.Draw(image)
    draw.text((10, 10), text, font=font_file, fill="red")

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")

    image_size = image.size
    return Response(
        buffer.getvalue(),
        media_type="image/png",
        headers={"x-image-size": f"{image_size[1]}x{image_size[0]}"},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
