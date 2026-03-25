import cv2

def detect_qr(file_path):
    try:
        img = cv2.imread(file_path)
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(img)

        return data if data else "No QR found"
    except:
        return "QR detection failed"