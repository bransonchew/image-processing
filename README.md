# Image Processing

---

Autopilot Tello EDU drone with face tracking and recognition, streamed on local netwwork.

## Getting Started

---

### Step 1:

Import and install conda dependencies by running:

```shell
conda env create -f environment.yml
```

### Step 2:

Prepare known face encodings using identity data and face images.

#### Option 1: Firebase

- Create Firebase project with Realtime Database and Storage
- Get service account credentials (json) from Firebase project settings 
  - In Realtime Database:
      - Seed `faces` data in database (See `example.json`)
  - In Storage:
      - Seed face images in `images` folder in root bucket 

Fetch and encode fetched data and face images by running:

```shell
python fetch.py
python encode.py
```

#### Option 2: Local assets folder

Prepare data and face images in `assets` and `assets/images` folders respectively, then run:

```shell
python encode.py
```

## Face Tracking & Recognition

---

To start face tracking and recognition using drone (see next section for streaming drone video):

```shell
python publish.py
```

Arguments:
- `--takeoff` drone takeoff or not
- `--export` enables exporting results (e.g. csv)
- `--verbose` enables verbose mode

or test the system using webcam with the `--webcam` flag:

```shell
python publish.py --webcam
```

## Streaming

---

To subscribe to video feed on local machine/process:

```shell
python subscribe.py
```

Arguments:
- `--record` record session or not (.avi)
- `--path` specify video recording path

To subscribe to video feed to view through browser, start the FastAPI server:

```shell
python api.py
```

This runs the server on localhost, to run on local network:

```shell
python api.py --host=0.0.0.0
```

## Acknowledgements

---

PID Face Tracking:

[Drone Programming With Python Course | 3 Hours | Including x4 Projects | Computer Vision](https://www.example.com)

Face Recognition:

[Recognize faces in live video using your webcam - Faster Version (Requires OpenCV to be installed)](https://github.com/ageitgey/face_recognition/blob/master/examples/facerec_from_webcam_faster.py)
