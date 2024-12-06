import socket

import imagezmq

from img.tracker import FPSTracker


class Publisher:
    def __init__(self, address='tcp://*:5555', calc_fps=True):
        # Image publishing
        self.sender = imagezmq.ImageSender(connect_to=address, REQ_REP=False)
        self.hostname = socket.gethostname()
        self.fps_tracker = FPSTracker() if calc_fps else None

    def publish(self, image) -> None:
        """Publish video frames"""

        # Publish image
        self.sender.send_image(self.hostname, image)

        # Optional FPS calculation
        if self.fps_tracker:
            fps = self.fps_tracker.update()
            print(f'FPS: {fps:.2f}')


def main() -> None:
    pass


if __name__ == '__main__':
    main()
