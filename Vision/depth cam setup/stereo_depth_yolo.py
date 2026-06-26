import cv2
import numpy as np
from ultralytics import YOLO

LEFT_URL  = "streamID"
RIGHT_URL = "streamID"

capL = cv2.VideoCapture(LEFT_URL)
capR = cv2.VideoCapture(RIGHT_URL)

BASELINE = 000# distance between dual cam setup (m)
FOCAL_LEN = 000# need calibration before deploy

stereo = cv2.StereoBM_create(numDisparities=96, blockSize=15)

model = YOLO("yolov8n.pt")
while True:
    retL, frameL = capL.read()
    retR, frameR = capR.read()
    if not retL or not retR:
        continue

    grayL = cv2.cvtColor(frameL, cv2.COLOR_BGR2GRAY)
    grayR = cv2.cvtColor(frameR, cv2.COLOR_BGR2GRAY)

    disparity = stereo.compute(grayL, grayR).astype(np.float32) / 16.0
    disparity[disparity <= 0.1] = 0.1

    depth = (FOCAL_LEN * BASELINE) / disparity

    results = model(frameL, conf=0.4)

    for r in results:
        for box in r.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cx = int((x1 + x2) / 2)
            cy = int((y1 + y2) / 2)

            distance = depth[cy, cx]

            label = f"{model.names[int(box.cls)]} {distance:.2f}m"
            cv2.rectangle(frameL, (x1,y1), (x2,y2), (0,255,0), 2)
            cv2.putText(frameL, label, (x1, y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 2)

    cv2.imshow("Stereo Depth", frameL)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capL.release()
capR.release()
cv2.destroyAllWindows()
