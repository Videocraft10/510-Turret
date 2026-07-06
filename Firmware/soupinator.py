#use this for 16 error: lsof | grep usbmodem101

# import cv2
# import serial
# import time
# import sys

# # --- CONFIGURATION ---
# SERIAL_PORT = "/dev/cu.usbmodem101" 
# BAUD = 115200
# SEND_INTERVAL = 0.04  # Speed up slightly to 40ms for higher tracking response

# try:
#     ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)
#     time.sleep(2)
# except Exception:
#     sys.exit(1)

# # Load both Frontal and Profile face tracking architectures
# face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
# profile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_profileface.xml")

# cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
# last_send = 0


# while True:
#     ret, frame = cap.read()
#     if not ret: continue
    
#     frame = cv2.flip(frame, 1)  # Natural mirror mapping
#     frame = cv2.resize(frame, (320, 240))
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
#     # Execute primary frontal scan with strict noise filtering
#     faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=10, minSize=(60, 60))
#     tracking_mode = "FRONT LOCK"
    
#     # Pass 2: Right Profile & Up/Down Tilt Scan (Loosened thresholds for better vertical tracking)
#     if len(faces) == 0:
#         faces = profile_cascade.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=5, minSize=(60, 60))
#         tracking_mode = "PROFILE RIGHT LOCK"
        
#     # Pass 3: Left Profile Scan (Tricks OpenCV by flipping the image horizontally in memory)
#     if len(faces) == 0:
#         flipped_gray = cv2.flip(gray, 1)
#         left_faces = profile_cascade.detectMultiScale(flipped_gray, scaleFactor=1.05, minNeighbors=5, minSize=(60, 60))
        
#         if len(left_faces) > 0:
#             # Mathematical inversion to map the coordinates back onto your normal screen space
#             for (lx, ly, lw, lh) in left_faces:
#                 cx_flipped = lx + lw // 2
#                 cx_normal = 320 - cx_flipped
#                 x = cx_normal - lw // 2
#                 y = ly
#                 w = lw
#                 h = lh
#             faces = [(x, y, w, h)]
#             tracking_mode = "PROFILE LEFT LOCK"
        
#     now = time.time()
#     if now - last_send > SEND_INTERVAL:
#         if len(faces) > 0:
#             x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
#             cx, cy = x + w // 2, y + h // 2
#             area = w * h
            
#             # Send live tracking packet
#             ser.write(f"{cx},{cy},{area}\n".encode())
            
#             # Draw green indicator box around the target
#             cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
#             cv2.circle(frame, (cx, cy), 4, (0, 0, 255), -1)
#             cv2.putText(frame, tracking_mode, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
#         else:
#             # Send lost notice (Arduino memory buffer handles position hold)
#             ser.write(b"0,0,0\n")
            
#         ser.flush()
#         last_send = now
        
#     # Calibration Crosshair Overlay
#     cv2.line(frame, (160, 110), (160, 130), (255, 255, 255), 1)
#     cv2.line(frame, (150, 120), (170, 120), (255, 255, 255), 1)
    
#     cv2.imshow("Advanced Target Acquisition System", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
# ser.close()

import cv2
import mediapipe as mp
import serial
import time
import sys
# --- CONFIGURATION ---
SERIAL_PORT = "/dev/cu.usbmodem101" 
BAUD = 115200
SEND_INTERVAL = 0.03  # Send tracking coordinates every 30ms
# --- PORT HANDLING & HANDSHAKE ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD, timeout=1)
    time.sleep(2)  # Stabilization delay for ESP32 boot cycle
except Exception as e:
    print(f"\n[!!!] PORT ERROR: Verify that the Arduino Serial Monitor is completely CLOSED! ({e})\n")
    sys.exit(1)
# --- INITIALIZE BLAZEFACE AI PIPELINE ---
mp_face_detection = mp.solutions.face_detection
# model_selection=0 is optimized for short-range camera tracking (< 2 meters)
face_detection = mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
last_send = 0
while True:
    ret, frame = cap.read()
    if not ret: 
        continue

    # 1. Flip horizontally so tracking directions mirror your body movements naturally
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (320, 240))

    # 2. Convert color space from OpenCV default BGR to MediaPipe AI native RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 3. Process frame through the local neural network
    results = face_detection.process(rgb_frame)

    target_found = False
    cx, cy, area = 0, 0, 0
    largest_area = 0
    best_bbox = None
    # 4. Filter and select target
    if results.detections:
        for detection in results.detections:
            # Extract proportional bounding markers from the model
            bboxC = detection.location_data.relative_bounding_box

            # Map proportional floats to explicit 320x240 pixel grids
            w = int(bboxC.width * 320)
            h = int(bboxC.height * 240)
            x = int(bboxC.xmin * 320)
            y = int(bboxC.ymin * 240)

            current_area = w * h

            # Filter noise and lock onto the single largest target in view
            if current_area > largest_area and w > 30 and h > 30:
                largest_area = current_area
                cx = x + w // 2
                cy = y + h // 2
                area = current_area
                best_bbox = (x, y, w, h)
                target_found = True
    # 5. Serial Transmission
    now = time.time()
    if now - last_send > SEND_INTERVAL:
        if target_found and best_bbox is not None:
            # Transmit standard coordinate packet to the ESP32
            ser.write(f"{cx},{cy},{area}\n".encode())

            # UI: Bounding box, target lock indicator, and tracking dot
            bx, by, bw, bh = best_bbox
            cv2.rectangle(frame, (bx, by), (bx + bw, by + bh), (0, 255, 0), 2)
        else:
            # Send standard lost packet so the hardware halts tracking safely
            ser.write(b"0,0,0\n")

        ser.flush()
        last_send = now

    cv2.imshow("Target Acquisition System", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
# Clean termination to prevent serial port locking on subsequent runs
face_detection.close()
cap.release()
cv2.destroyAllWindows()
ser.close()