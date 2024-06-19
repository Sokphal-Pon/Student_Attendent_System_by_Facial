import cv2
import dlib
import numpy as np
import pickle
import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# Initialize Firebase
cred = credentials.Certificate("dir_firebase/databasestore.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://studentdata-e92be-default-rtdb.firebaseio.com/",
    'storageBucket': "studentdata-e92be.appspot.com"
})

# Importing student images
folderPath = 'students'
pathList = os.listdir(folderPath)
print(pathList)
imgList = []
studentID = []
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentID.append(os.path.splitext(path)[0])

    fileName = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName)

print(studentID)

# Load dlib's face detector and face recognition model
detector = dlib.cnn_face_detection_model_v1('Dlib\mmod_human_face_detector.dat')
sp = dlib.shape_predictor('Dlib\shape_predictor_68_face_landmarks.dat')
facerec = dlib.face_recognition_model_v1('Dlib\dlib_face_recognition_resnet_model_v1.dat')

def findEncodings(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        dets = detector(img, 1)
        if len(dets) == 0:
            print("No face detected in image.")
            continue
        for det in dets:
            shape = sp(img, det.rect)
            face_descriptor = facerec.compute_face_descriptor(img, shape)
            encode = np.array(face_descriptor)
            encodeList.append(encode)

    return encodeList

print("Encoding Started ...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentID]
print("Encoding Complete")

file = open("endCodingFace.p", 'wb')
pickle.dump(encodeListKnownWithIds, file)
file.close()
print("File Saved")
