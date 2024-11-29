import cv2

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    print("Kamera tidak terdeteksi.")
else:
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imshow("Kamera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

