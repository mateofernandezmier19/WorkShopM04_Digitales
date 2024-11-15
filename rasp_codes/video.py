import cv2
import requests
import numpy as np

# URL de la ESP32-CAM (ajusta la IP según tu configuración)
esp32_cam_url = 'http://192.168.20.39/cam-hi.jpg'

# Crear una ventana para mostrar el video
cv2.namedWindow("ESP32-CAM Video", cv2.WINDOW_NORMAL)

try:
    while True:
        # Solicita una imagen a la ESP32-CAM
        response = requests.get(esp32_cam_url, timeout=5)  # Timeout de 5 segundos
        if response.status_code == 200:
            # Convertir los datos de la respuesta a un arreglo numpy
            img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            # Mostrar la imagen en la ventana
            cv2.imshow("ESP32-CAM Video", frame)

            # Salir si se presiona la tecla 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            print(f"Error al obtener la imagen: {response.status_code}")
except Exception as e:
    print("Error al conectarse con la ESP32-CAM:", e)
finally:
    # Cierra la ventana
    cv2.destroyAllWindows()