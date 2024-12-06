import cv2
import imagezmq


class Subscriber:
    def __init__(self, address='tcp://localhost:5555'):
        # Image subscriber
        self.receiver = imagezmq.ImageHub(open_port=address, REQ_REP=False)

    def get_latest_frame(self):
        """Receive the latest frame from the publisher."""
        return self.receiver.recv_image()


def main() -> None:
    # Show streamed images until Ctrl-C
    sub = Subscriber()
    while True:
        name, frame = sub.get_latest_frame()
        cv2.imshow(name, frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == '__main__':
    main()
