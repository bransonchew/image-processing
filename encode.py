import json
import pickle
from pathlib import Path

import cv2
from face_recognition import face_encodings


# Directory to access images and data
DIR = Path('assets')


def get_encodings(img):
    return face_encodings(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))[0]


def encode_images(data: dict, pickle_file='encodings.pkl'):
    # Encode images
    encodings = [
        get_encodings(
            cv2.imread(DIR / f"images/{val['image_path']}")
        )
        for val in data.values()
    ]

    # Pickle encodings with ids
    data = encodings, list(data.keys())
    with open(DIR / pickle_file, 'wb') as f:
        pickle.dump(data, f)


def main():
    # Pair face images with identity data
    with open(DIR / 'data.json', 'r') as f:
        data = json.load(f)

    # Encode face images with ids
    encode_images(data=data)

    # Verify
    with open(DIR / 'encodings.pkl', 'rb') as f:
        en, ids = pickle.load(f)
    print(ids)


if __name__ == '__main__':
    main()
