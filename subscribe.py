import argparse
import time

import cv2

from img.subscriber import Subscriber


# Color definitions
BLUE = (255, 0, 0)
WHITE = (255, 255, 255)


def subscribe(record=False, output_file='output.avi') -> None:
    # Image stream subscriber
    sub = Subscriber()

    # Video recorder setup
    name, frame = sub.get_latest_frame()
    height, width, _ = frame.shape

    # Start timer
    start = time.time()

    if record:
        out = cv2.VideoWriter(output_file,
                              cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                              25,
                              (width, height))
        print('Recording in progress')

    try:
        # Stream images/video
        while True:
            name, frame = sub.get_latest_frame()

            # Calculate elapsed time since the start
            elapsed_time = time.time() - start
            elapsed_time_str = time.strftime('%M:%S', time.gmtime(elapsed_time))

            # Set position for the text and rectangle (bottom left corner)
            text_position = (20, height - 12)
            rectangle_start = (5, height - 45)  # Top-left corner of the rectangle
            rectangle_end = (150, height - 5)  # Bottom-right corner of the rectangle

            # Draw red rectangle (filled) at the bottom-left of the frame
            cv2.rectangle(frame, rectangle_start, rectangle_end, BLUE, cv2.FILLED)

            # Add the white text (elapsed time) on top of the red rectangle
            cv2.putText(frame, f'{elapsed_time_str}', text_position,
                        cv2.FONT_HERSHEY_SIMPLEX, 1, WHITE, 2, cv2.LINE_AA)

            # Record video
            if record:
                out.write(frame)

            # Display video
            cv2.imshow(name, frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print('Subscription interrupted')

    finally:
        if record:
            out.release()
            print('Recording stopped')
        cv2.destroyAllWindows()


def main() -> None:
    # Create argument parser
    parser = argparse.ArgumentParser(description="Face tracking and recognition subscribing script")

    # Optional argument
    parser.add_argument('-p', '--path', type=str, default="output.avi", help="Video recording file path")

    # Boolean flags
    parser.add_argument('--record', action='store_true', help="Enable video recording")

    # Parse the arguments
    args = parser.parse_args()

    # Start video stream subscription
    subscribe(record=args.record, output_file=args.path)


if __name__ == '__main__':
    main()
