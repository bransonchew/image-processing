import json
from pathlib import Path
from typing import Iterable

import firebase_admin
from firebase_admin import credentials, storage, db


# Directory to store images and data
DIR = Path('assets')


def get_face_data():
    # Fetch data
    ref = db.reference('faces')
    data = ref.get()

    # Save data
    with open(DIR / 'data.json', 'w') as f:
        json.dump(data, f, indent=2)

    return data


def get_face_images(image_paths: Iterable[str]) -> None:
    # Make tmp images directory
    Path.mkdir(DIR / 'images', exist_ok=True)

    # Get a reference to the Firebase Storage bucket
    bucket = storage.bucket()

    for path in image_paths:
        # Blob represents the image object in the Firebase Storage bucket
        blob = bucket.blob(f'images/{path}')

        # Download the image to the local directory
        blob.download_to_filename(DIR / 'images' / path)


def main():
    # Init firebase app
    cred = credentials.Certificate('key.json')
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://chimera-47012-default-rtdb.asia-southeast1.firebasedatabase.app/',
        'storageBucket': 'chimera-47012.appspot.com',
    })

    # Fetch people details and images
    data = get_face_data()
    get_face_images(val['image_path'] for key, val in data.items())


if __name__ == '__main__':
    main()
