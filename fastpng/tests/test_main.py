from fastapi.testclient import TestClient
import os

from ..main import app
import base64


client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_read_fonts():
    response = client.get("/fonts")
    assert response.status_code == 200
    # Depending on the system, the fonts might be different so we test that a list is returned instead of the actual content
    assert isinstance(response.json(), list)


def test_generate_image():
    response = client.get("/generate_image?font=Arial&font_size=12&text=Hello+World")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.headers["Content-Length"] == "1922"
    assert response.headers["x-image-size"] == "256x512"
    # test that the image is a valid PNG
    assert base64.b64encode(response.content).startswith(
        b"iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAA"
    )
