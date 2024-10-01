import cv2
import os
import pickle
import numpy as np
import face_recognition
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': "https://face-recognition-1bf72-default-rtdb.firebaseio.com/",
    'storageBucket': "face-recognition-1bf72.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4, 480)

imgBackground =  cv2.imread('Resources/background.png')

# Import img into list
folderModePath = 'Resources/Modes'
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath,path)))

# print(len(imgModeList)) -> Mengecek keterangan absensi

#Load encoding file
print("Loading Encode File ...")
file = open('EncodeFile.p', 'rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, studentIds = encodeListKnownWithIds
#print(studentIds)
print("Encode File Loaded")

modeType = 0
counter = 0
id = -1
imgStudent = []

try:
    while True:
        success, img = cap.read()


        if not success:
            print("Failed to grab frame")
            break

        imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
        imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

        faceCurFrame = face_recognition.face_locations(imgS) #Deteksi muka
        encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)
        #Convert ke RGB utk face_recognition

        imgBackground[162:162 + 480, 55:55 + 640] = img
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
            matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
            faceDistance = face_recognition.face_distance(encodeListKnown, encodeFace)
            # print("matches", matches)
            # print("faceDistance", faceDistance)

            matchIndex = np.argmin(faceDistance)
            # print("Match Index", matchIndex)

            if matches[matchIndex]:
                # print("Known Face Detected")
                # print(studentIds[matchIndex])

                #Jika ketemu muka, buat box
                y1, x2, y2, x1 = faceLoc
                #Di scale back up
                y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4

                bbox = (55 + x1, 162 + y1, (x2 - x1), (y2 - y1))
                imgBackground = cvzone.cornerRect(imgBackground, bbox, rt=0)

                # # Fetch student info from Firebase
                # studentInfo = db.reference(f'Students/{id}').get()
                #
                # # Now that the data is fetched, you can display the student's name
                # if studentInfo:
                #     cvzone.putTextRect(imgBackground, studentInfo['name'], (300, 700), scale=2, thickness=2,
                #                        offset=10)
                #
                # cv2.imshow("Face Attendance", imgBackground)
                # cv2.waitKey(1)

                id = studentIds[matchIndex]
                print(id)

                if counter == 0:
                    cvzone.putTextRect(imgBackground, "Loading", (400, 400))
                    cv2.imshow("Face Attendance", imgBackground)
                    cv2.waitKey(1)



                    counter = 1
                    modeType = 1

        if counter != 0:

            if counter == 1:
                studentInfo = db.reference(f'Students/{id}').get()
                print(studentInfo)

                #Get image from storage in FireBase
                blob = bucket.get_blob(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgStudent = cv2.imdecode(array, cv2.COLOR_BGRA2BGR)

                #Update data of attendance
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                              "%Y-%m-%d %H:%M:%S")
                secondElapsed = (datetime.now()-datetimeObject).total_seconds()
                print(secondElapsed)


                #ntar di convert ke brp jam tiap matkul
                if secondElapsed < 60:



                    #Untuk update database
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

            if 15<counter<30:
                modeType = 2
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

            #Timer
            if counter <=15:
                cv2.putText(imgBackground,str(studentInfo['total_attendance']),(861,125),
                            cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                cv2.putText(imgBackground, str(studentInfo['major']), (1006, 550),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(id), (1006, 493),
                            cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
                cv2.putText(imgBackground, str(studentInfo['standing']), (910, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo['binusian_year']), (1015, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(imgBackground, str(studentInfo['semester']), (1125, 625),
                            cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)


                (w,h), _ =cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                offset = (414-w)//2
                cv2.putText(imgBackground, str(studentInfo['name']), (808+offset, 445),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

                imgBackground[175:175+216,909:909+216] = imgStudent

            counter+=1

            if counter >= 30:
                counter = 0
                modeType = 0
                studentInfo = []
                imgStudent = []
                imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        # cv2.imshow("Webcam", img)
        cv2.imshow("Face Attendance", imgBackground)

        # Press 'q' to exit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
except KeyboardInterrupt:
    print("Program interrupted by user.")

# Release camera and close windows
finally:
    cap.release()
    cv2.destroyAllWindows()