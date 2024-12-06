""""
Webcam controller implementation for testing operations without involving drone

"""

import json
import pickle

import cv2
import face_recognition
import numpy as np
import pandas as pd

from img.publisher import Publisher
from img.singleton import Singleton


# Color definitions
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Maximum allowed speed on Tello
MAX_SPEED = 100


class WebcamController(metaclass=Singleton):
    """Handles webcam and CV operations"""

    # Frame dimensions and PID control parameters
    SCALE_FACTOR = 0.25
    WIDTH = SCALE_FACTOR * 1920
    HEIGHT = SCALE_FACTOR * 1080
    FB_RANGE = (6200, 6800)
    PID_YAW = (0.8, 0.8, 0.1)  # yaw control
    PID_ALT = (0.3, 0.3, 0.1)  # altitude control

    def __init__(self, verbose=True, assets_path='../assets'):
        # Publisher
        self.pub = Publisher(calc_fps=verbose)

        # Face cascade
        self.cascade = cv2.CascadeClassifier(
            f'{assets_path}/haarcascades/haarcascade_frontalface_default.xml'
        )

        # PID errors
        self.error_yaw = 0
        self.error_alt = 0
        self.verbose = verbose

        print(f'Fetching face images and data...')

        print(f'Encoding faces...')

        # Face encodings & data
        with open(f'{assets_path}/encodings.pkl', 'rb') as f:
            self.known_face_encodings, self.known_face_ids = pickle.load(f)
        with open(f'{assets_path}/data.json', 'r') as f:
            self.known_face_data = json.load(f)

        # Face recognition confidence
        self.tolerance = 0.5
        self.detections = {face_id: 0 for face_id in self.known_face_ids}
        self.detections['Unknown'] = 0  # Unknown face

    def track(self, frame):
        """Tracks faces and calculates movement adjustments"""

        # Locate faces
        img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.cascade.detectMultiScale(img_gray, 1.2, 8)
        centre = 0, 0
        area = 0

        # Largest face
        for x, y, w, h in faces:
            cx = x + w // 2
            cy = y + h // 2
            a = w * h
            if a > area:
                centre = (cx, cy)
                area = a

        # Face center coordinates & dims
        x, y = centre
        w, h = self.WIDTH, self.HEIGHT

        # PID errors
        error_yaw = x - w // 2
        error_alt = h // 2 - y

        # Calculate speed for yaw (left/right) and altitude (up/down)
        yaw = self.PID_YAW[0] * error_yaw + self.PID_YAW[1] * (error_yaw - self.error_yaw)
        alt = self.PID_ALT[0] * error_alt + self.PID_ALT[1] * (error_alt - self.error_alt)

        # Clip speeds to maximum limits
        yaw = int(np.clip(yaw, -MAX_SPEED, MAX_SPEED))
        alt = int(np.clip(alt, -MAX_SPEED, MAX_SPEED))

        # Forward/backward speed based on face area
        fwd = 0
        if self.FB_RANGE[0] <= area <= self.FB_RANGE[1]:
            fwd = 0
        elif area > self.FB_RANGE[1]:
            fwd = -20  # Move backwards
        elif area < self.FB_RANGE[0] and area != 0:
            fwd = 20  # Move forwards

        # If no face detected, stop movements
        if x == 0 and y == 0:
            yaw, error_yaw = 0, 0
            alt, error_alt = 0, 0

        # Cache errors
        self.error_yaw, self.error_alt = error_yaw, error_alt

        # Log velocities
        if self.verbose:
            print(f'{yaw = :<6}, {alt = :<6}, {fwd = :<6}')

    def recognize(self, frame):
        """Recognizes faces within frame"""

        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding,
                                                     tolerance=self.tolerance)
            name = 'Unknown'

            # Use the known face with the shortest distance to the new face
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                face_id = self.known_face_ids[best_match_index]
                name = self.known_face_data[face_id]['name']

            face_names.append(name)
            self.detections[face_id if name != 'Unknown' else name] += 1

        return face_locations, face_names

    def start(self, export=False):
        """Starts face recognition and tracking using drone video"""

        # Webcam setup
        cap = cv2.VideoCapture(0)

        # Initialize variables
        process_this_frame = True
        total = 0
        scale = WebcamController.SCALE_FACTOR

        try:
            while True:
                # Grab a single frame of video
                ret, frame = cap.read()
                if not ret:
                    continue

                # Resize frame for faster processing
                small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)

                # Only process every other frame to save time
                if process_this_frame:
                    # Invert webcam RGB
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

                    # Face recognition
                    face_locations, face_names = self.recognize(rgb_small_frame)

                    # Track total detection instances
                    total += 1

                process_this_frame = not process_this_frame

                # Display the results
                for (top, right, bottom, left), name in zip(face_locations, face_names):

                    # Scale back up face locations since the frame we detected in was scaled
                    top = int(top // scale)
                    right = int(right // scale)
                    bottom = int(bottom // scale)
                    left = int(left // scale)

                    # Authorization
                    if name != 'Unknown':
                        colour, text_colour = GREEN, BLACK
                    else:
                        colour, text_colour = RED, WHITE

                    # Draw a box around the face
                    cv2.rectangle(frame, (left, top), (right, bottom), colour, 2)

                    # Draw a label with a name below the face
                    cv2.rectangle(frame, (left, bottom - 35), (right, bottom), colour, cv2.FILLED)
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, text_colour, 1)

                # Face tracking
                self.track(small_frame)

                # Publish image
                self.pub.publish(frame)

        except KeyboardInterrupt:
            print('Streaming stopped by user')

        finally:
            cap.release()
            print('Video capture resource released')

            # Export detections for metrics
            if export:
                self.detections['total'] = total
                df = pd.DataFrame(list(self.detections.items()), columns=['face_id', 'detection_count'])
                df.to_csv('detections.csv', index=False)


def main() -> None:
    controller = WebcamController(verbose=True)
    controller.start(export=False)


if __name__ == '__main__':
    main()
