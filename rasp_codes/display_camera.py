import numpy as np
import urllib.request
import cv2
import time

url = 'http://192.168.137.21/cam-hi.jpg'

while True:
    try:
        # Fetch the image
        imgResponse = urllib.request.urlopen(url, timeout=10)
        imgNp = np.array(bytearray(imgResponse.read()), dtype=np.uint8)
        frame = cv2.imdecode(imgNp, cv2.IMREAD_COLOR)

        if frame is not None:
            # Display the image
            cv2.imshow("ESP32-CAM", frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    except Exception as e:
        print(f"Error fetching image: {e}")
    
    # Fetch image at a 25ms interval
    time.sleep(0.005)

# Release display window resources
cv2.destroyAllWindows()