import cv2
import numpy as np
import os
import time
import requests
import json
from PIL import Image
import RPi.GPIO as GPIO

try:
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(7, GPIO.OUT)
    GPIO.setup(7,GPIO.LOW)
    
    req = None

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read('/home/pi/FaceRec/trainer/trainer.yml')
    cascadePath = "/home/pi/opencv-3.4.1/data/haarcascades/haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(cascadePath)
     
    font = cv2.FONT_HERSHEY_SIMPLEX

    id = 0
     
    # names related to ids: example ==> Zhaohui: id=1,  etc
    names = ['None', 'Zhaohui']

    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)

    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)

    while True:
        req = requests.get("https://api.thingspeak.com/channels/785685/feeds/last.json?api_key=ISSHCUI0FW475BY9")
        print(req.text)
        result = json.loads((req.text))
        print(result['field1']) 
        GPIO.setup(7,GPIO.LOW)
        if (result['field1'] == "1"):
            print("Recgnize your face...")
            while True:
                ret, img =cam.read()
                gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
             
                face = faceCascade.detectMultiScale( 
                    gray,
                    scaleFactor = 1.2,
                    minNeighbors = 5,
                    minSize = (int(minW), int(minH)),
                   )
                
                for(x,y,w,h) in face:
                    
                    cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
                    id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
                    
                    if (confidence > 20):
                        id = names[id]
                        confidence = "  {0}%".format(round(100 - confidence))
                        
                        print("Face recgnized")
                        cv2.imshow('camera',img)
                        GPIO.setup(7,GPIO.HIGH)
                        
                    else:
                        id = "unknown"
                        confidence = "  {0}%".format(round(100 - confidence))
                        RequestThingSpeak = 'https://api.thingspeak.com/update?api_key=XHTN7TCLMJQ5454X&field1=4'
                        request = requests.get(RequestThingSpeak)
                        print(request.text)
                        print("Face not recgnized")
                        cv2.imshow('camera',img)

                    cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)

                cv2.imshow('camera',img)
                k = cv2.waitKey(10) & 0xff # Press 'ESC' for exiting video
                if k == 27:
                    break

            RequrstIFTTT = 'https://maker.ifttt.com/trigger/LockOn/with/key/cnzNlWvuMMqnxqCAJCAcwv&value1=Unlock'
            request = requests.get(RequestIFTTT)
            print(request.text)
            print("Unlock")
            print("\n [INFO] Exiting Program and cleanup stuff")
            cam.release()
            cv2.destroyAllWindows()
        elif (result['field1'] == "2"):
            # For each person, enter one numeric face id
            face_id = input('\n enter user id end press <return> ==>  ')
            
            print("\n [INFO] Initializing face capture. Look the camera and wait ...")
            # Initialize individual sampling face count
            count = 0
            while(True):
                ret, img = cam.read()
            #    img = cv2.flip(img, -1) # flip video image vertically
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(gray, 1.3, 5)
                
                for (x,y,w,h) in faces:
                    cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
                    count += 1
            
                    # Save the captured image into the datasets folder
                    cv2.imwrite("dataset/User." + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
            
                    cv2.imshow('image', img)
            
                k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
                if k == 27:
                    break
                elif count >= 30: # Take 30 face sample and stop video
                    break
            
            # Do a bit of cleanup
            print("\n [INFO] Exiting Program and cleanup stuff")
            cam.release()
            cv2.destroyAllWindows()

            path = '/home/pi/FaceRec/dataset'
            def getImagesAndLabels(path):
                imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
                faceSamples=[]
                ids = []
                for imagePath in imagePaths:
                    PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
                    img_numpy = np.array(PIL_img,'uint8')
                    id = int(os.path.split(imagePath)[-1].split(".")[1])
                    faces = faceCascade.detectMultiScale(img_numpy)
                    for (x,y,w,h) in faces:
                        faceSamples.append(img_numpy[y:y+h,x:x+w])
                        ids.append(id)
                return faceSamples,ids
            print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
            faces,ids = getImagesAndLabels(path)
            recognizer.train(faces, np.array(ids))
            
            # Save the model into trainer/trainer.yml
            recognizer.write('/home/pi/FaceRec/trainer/trainer.yml') # recognizer.save() worked on Mac, but not on Pi
            
            # Print the numer of faces trained and end program
            print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
                
        elif (result['field1'] == "3"):
            GPIO.setup(7,GPIO.HIGH)
            print("Unlock")

        elif (result['field1'] == "4"):                                          
            GPIO.setup(7,GPIO.LOW)
            print("Lock")

except KeyboardInterrupt:
    exit()