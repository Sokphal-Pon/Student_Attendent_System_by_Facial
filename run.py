import sys
import cv2
import dlib
import os
import pickle
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials, db, storage
from PyQt5.QtCore import QTimer, Qt, QDateTime
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QDesktopWidget
from PyQt5 import QtCore, QtGui, QtWidgets
import csv
from datetime import datetime, timedelta

# Initialize Firebase
cred = credentials.Certificate("dir_firebase/databasestore.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://studentdata-e92be-default-rtdb.firebaseio.com/",
    'storageBucket': "studentdata-e92be.appspot.com"
})

# Load training facial encodings and student IDs
with open('endCodingFace.p', 'rb') as file:
    encodeListKnownWithIds = pickle.load(file)
encodeListKnown, studentID = encodeListKnownWithIds
print("Model is Loading...")

# Dictionary to keep track of the last scan time
last_scan_time = {}


class Ui_sudent_info(object):
    def setupUi(self, sudent_info, data, main_window):
        self.main_window = main_window
        self.data = data
        self.sudent_info_window = sudent_info

        sudent_info.setObjectName("sudent_info")
        sudent_info.setFixedSize(620, 800)  # Make the window unresizable
        
        font = QtGui.QFont()
        font.setPointSize(10)
       
        self.image_label = QLabel(sudent_info)
        self.image_label.setGeometry(QtCore.QRect(210, 30, 195, 195))  # Image size
        self.image_label.setStyleSheet("border: 2px solid black;")
        self.load_student_image(data.get("id", ""))

        labels = {
            "label": ("ID:", 220, 250),
            "fname": ("First Name:", 70, 360),
            "lname": ("Last Name:", 330, 360),
            "major": ("Major:", 70, 400),
            "fuculity": ("Faculty:", 330, 400),
            "address": ("Address:", 70, 440),
            "Acyear": ("Academic Year:", 140, 590),
            "tAttendance": ("Total Attendance:", 360, 590),
            "email": ("Email:", 70, 480),
            "email_2": ("Last Attendance:", 70, 520),
        }

        for key, value in labels.items():
            label = QtWidgets.QLabel(sudent_info)
            label.setGeometry(QtCore.QRect(value[1], value[2], 200, 16)) # relocation of line-sharp
            label.setFont(font)
            label.setText(value[0])
            setattr(self, key, label)
        
        self.lineEdit_9 = self.create_line_edit(sudent_info, 250, 246, str(data.get("id", "")))
        self.lineEdit_9.setObjectName("lineEdit_9")
        
        self.lineEdit = self.create_line_edit(sudent_info, 155, 355, data.get("fist_name", ""))
        self.lineEdit_2 = self.create_line_edit(sudent_info, 415, 355, data.get("last_name", ""))
        self.lineEdit_3 = self.create_line_edit(sudent_info, 155, 395, data.get("major", ""))
        self.lineEdit_4 = self.create_line_edit(sudent_info, 415, 395, data.get("fuculity", ""))
        self.lineEdit_5 = self.create_line_edit(sudent_info, 155, 475, data.get("email", ""))
        self.lineEdit_6 = self.create_line_edit(sudent_info, 155, 435, data.get("address", ""))
        self.lineEdit_7 = self.create_line_edit(sudent_info, 140, 620, data.get("acadimac_year", ""))
        self.lineEdit_8 = self.create_line_edit(sudent_info, 360, 620, str(data.get("total_attendance", "")))
        self.lineEdit_10 = self.create_line_edit(sudent_info, 190, 515, data.get("last_time_scan", ""))

        # Set the relevant QLineEdit elements to read-only
        self.lineEdit_9.setReadOnly(True)
        self.lineEdit.setReadOnly(True)
        self.lineEdit_2.setReadOnly(True)
        self.lineEdit_3.setReadOnly(True)
        self.lineEdit_4.setReadOnly(True)
        self.lineEdit_5.setReadOnly(True)
        self.lineEdit_6.setReadOnly(True)
        self.lineEdit_7.setReadOnly(True)
        self.lineEdit_8.setReadOnly(True)
        self.lineEdit_10.setReadOnly(True)
        
        self.pushButton_2 = QtWidgets.QPushButton(sudent_info)
        self.pushButton_2.setGeometry(QtCore.QRect(270, 730, 101, 31))
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_save")
        self.pushButton_2.setText("Save")
        self.pushButton_2.clicked.connect(self.save_info)
        
        self.retranslateUi(sudent_info)
        QtCore.QMetaObject.connectSlotsByName(sudent_info)
    
    def create_line_edit(self, sudent_info, x, y, text):
        line_edit = QtWidgets.QLineEdit(sudent_info)
        line_edit.setGeometry(QtCore.QRect(x, y, 150, 25))  # resize info line
        line_edit.setText(str(text))  # Ensure text is converted to string
        return line_edit

    def retranslateUi(self, sudent_info):
        _translate = QtCore.QCoreApplication.translate
        sudent_info.setWindowTitle(_translate("sudent_info", "Information"))

    def load_student_image(self, id):
        stor = storage.bucket().blob(f'students/{id}.png')
        array = np.frombuffer(stor.download_as_string(), np.uint8)
        imgStudents = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if imgStudents is not None:
            imgStudents = cv2.cvtColor(imgStudents, cv2.COLOR_BGR2RGB)
            h, w, ch = imgStudents.shape
            bytes_per_line = ch * w
            qimg = QImage(imgStudents.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(qimg).scaled(200, 200, Qt.KeepAspectRatio))

    def save_info(self):
        student_id = self.lineEdit_9.text()
        current_time = datetime.now()

        last_scan_time[student_id] = current_time

        # Gather data from the form fields
        data_to_save = {
            "id": self.lineEdit_9.text(),
            "fist_name": self.lineEdit.text(),
            "last_name": self.lineEdit_2.text(),
            "major": self.lineEdit_3.text(),
            "fuculity": self.lineEdit_4.text(),
            "email": self.lineEdit_5.text(),
            "address": self.lineEdit_6.text(),
            "total_attendance": self.lineEdit_8.text(),
            "last_time_scan": self.lineEdit_10.text()
        }
        
        # Save the data to a CSV file
        with open('student_attendanced.csv', 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = data_to_save.keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            if csvfile.tell() == 0:
                writer.writeheader()  # Write header only if file is empty
            writer.writerow(data_to_save)
        
        QMessageBox.information(None, "Save", "Information saved successfully!")
        self.go_back()  # Go back to the main window after saving

    def go_back(self):
        # Close the current window and return to the webcam window
        self.sudent_info_window.close()
        self.main_window.start_recognition()
        self.main_window.show()

class WebcamWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("STUDENT ATTENDANCE SYSTEM")
        self.resize(1080, 720)  # Set the initial window size
        self.center()

        # Create a label to display the webcam feed
        self.label = QLabel(self)
        self.setCentralWidget(self.label)
        self.label.setFixedSize(1080, 720)  # Set the label size to match the resolution

        # Create a QTimer to update the webcam feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(10)

        # Open the webcam
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("Error: Could not open webcam.")
            exit()

        # Set the resolution to 1080x720
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1080)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

        self.counter = 0
        self.id = -1

        # Load the face detector and face recognition model
        self.detector = dlib.get_frontal_face_detector()
        self.sp = dlib.shape_predictor('Dlib/shape_predictor_68_face_landmarks.dat')
        self.facerec = dlib.face_recognition_model_v1('Dlib/dlib_face_recognition_resnet_model_v1.dat')

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def start_recognition(self):
        self.counter = 0
        self.id = -1
        self.timer.start(30)  # Restart the timer

    def update_frame(self):
        success, img = self.cap.read()
        if not success:
            return
        img = cv2.resize(img, (1080, 720))
        imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)
        
        detections = self.detector(imgS)
        encodeCurFrame = [self.facerec.compute_face_descriptor(imgS, self.sp(imgS, det)) for det in detections]
        
        for encodeFace, det in zip(encodeCurFrame, detections):
            matches = [np.linalg.norm(np.array(encodeListKnown[i]) - np.array(encodeFace)) for i in range(len(encodeListKnown))]
            matchIndex = np.argmin(matches)
            
            if matches[matchIndex] < 0.6:  # Adjust threshold as needed
                face_recognized = True
                x1, y1, x2, y2 = det.left(), det.top(), det.right(), det.bottom()
                boundingBox = (x1 * 4, y1 * 4, (x2 - x1) * 4, (y2 - y1) * 4)  # Scale back to original size
                self.id = studentID[matchIndex]

                current_time = datetime.now()
                if self.id in last_scan_time:
                    elapsed_time = current_time - last_scan_time[self.id]
                    if elapsed_time < timedelta(hours=1):       # Waitting for 1 hours to attendance again
                        cvzone.cornerRect(img, boundingBox, l=30, t=5, rt=0)  # Draw rectangle
                        cv2.putText(img, "You're already Attendance", (x1 * 4, y1 * 4 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        self.counter = 0  # Reset counter to avoid showing info window
                        continue

                last_scan_time[self.id] = current_time

                # Update Firebase database
                ref = db.reference(f'students/{self.id}')
                studentInfo = ref.get()
                total_attendance = int(studentInfo.get('total_attendance', 0)) + 1
                last_time_scan = current_time.strftime("%Y-%m-%d %H:%M:%S")
                
                ref.update({
                    'total_attendance': total_attendance,
                    'last_time_scan': last_time_scan
                })

                self.counter = 1  # Face recognized

        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        h, w, ch = img.shape
        bytes_per_line = ch * w
        qimg = QImage(img.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.label.setPixmap(QPixmap.fromImage(qimg))

        if self.counter != 0:
            if self.counter == 1:
                Ui_sudent_info_data = db.reference(f'students/{self.id}').get()
                Ui_sudent_info_data["id"] = self.id
                Ui_sudent_info_data["last_time_scan"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.show_student_info(Ui_sudent_info_data)
                self.counter = 0  # Reset counter to avoid repeating

    def show_student_info(self, Ui_sudent_info_data):
        self.timer.stop()  # Stop the timer when showing the info window
        self.hide()
        self.info_window = QMainWindow()
        self.ui = Ui_sudent_info()
        self.ui.setupUi(self.info_window, Ui_sudent_info_data, self)
        self.info_window.show()

    def closeEvent(self, event):
        self.cap.release()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WebcamWindow()
    window.show()
    sys.exit(app.exec_())
