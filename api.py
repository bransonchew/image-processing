import argparse

import cv2
import uvicorn
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

from img.subscriber import Subscriber
from utils import get_ip_address


app = FastAPI()


def generate_frames():
    """Generator to yield frames as JPEG-encoded bytes."""

    # Subscribe to video stream
    sub = Subscriber()
    while True:
        name, frame = sub.get_latest_frame()

        # Encode the frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = buffer.tobytes()

        # Yield the frame as a multipart response (MJPEG format)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.get("/")
async def index():
    """API endpoint to stream video frames."""
    return StreamingResponse(generate_frames(),
                             media_type="multipart/x-mixed-replace; boundary=frame")


@app.get("/hello/{name}")
def hello(name: str):
    return {'message': f'Hello {name}!'}


if __name__ == "__main__":
    # Create argument parser
    parser = argparse.ArgumentParser(description="Run a FastAPI server with options.")

    # Boolean flags
    parser.add_argument('--reload', action='store_true', default=True, help="Enable auto-reload")
    parser.add_argument('--no-reload', action='store_false', dest='reload', help="Enable auto-reload")

    # Optional arguments
    parser.add_argument('--host', type=str, default='127.0.0.1', help="The host IP to bind the server to")
    parser.add_argument('--port', type=int, default=8000, help="The port to bind the server to (default: 8000)")

    # Parse the arguments
    args = parser.parse_args()

    # URL display
    ip_address = get_ip_address()
    url = f"http://{ip_address if args.host == '0.0.0.0' else args.host}:{args.port}"

    # Display server settings
    print(f"Starting FastAPI server on {url}")
    print(f"Reload: {'enabled' if args.reload else 'disabled'}")

    # Run the FastAPI server with uvicorn
    uvicorn.run(
        "api:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
