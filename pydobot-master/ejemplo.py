import cv2
import numpy as np
from serial.tools import list_ports
import pydobot

# Definir límites seguros para el brazo Dobot
MIN_X, MAX_X = 187.8, 313.4
MIN_Y, MAX_Y = -96.4, 97.3
MIN_Z, MAX_Z = -102.7, 120.7

# Inicializar el dispositivo Dobot
available_ports = list_ports.comports()
print(f'available ports: {[x.device for x in available_ports]}')
port = available_ports[2].device
device = pydobot.Dobot(port=port, verbose=True)

# Obtener y mostrar la pose inicial del brazo
(x, y, z, r, j1, j2, j3, j4) = device.pose()
print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

# Función para mover el brazo a la posición inicial
def Pos_Inicial():
    j1 = 0
    j2 = 15
    j3 = 0
    device.move_to(j1, j2, j3, j4, wait=True)
    device.wait(500)
    return j1, j2, j3

# Función para detectar un color en un frame
def detectColor(frame, hsvframe, lower, upper, color, texto):
    lower_bound = np.array(lower, np.uint8)
    upper_bound = np.array(upper, np.uint8)

    color_mask = cv2.inRange(hsvframe, lower_bound, upper_bound)
    kernel = np.ones((5, 5), "uint8")
    color_mask = cv2.dilate(color_mask, kernel)
    res_color = cv2.bitwise_and(frame, frame, mask=color_mask)

    contours, _ = cv2.findContours(color_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for pic, cont in enumerate(contours):
        area = cv2.contourArea(cont)
        if area > 300:
            x, y, w, h = cv2.boundingRect(cont)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, texto, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, color)
            return True  # Color detectado
    return False  # Color no detectado

# Configurar la cámara
cap = cv2.VideoCapture(0)

# Mover el brazo a la posición inicial
j1, j2, j3 = Pos_Inicial()

# Bucle principal para detección de color y control del brazo
while True:
    _, frame = cap.read()
    hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Detección del color azul
    azul_detectado = detectColor(frame, hsvframe, [94, 80, 2], [120, 255, 255], [255, 0, 0], "azul")

    # Control del dispositivo de succión basado en la detección del color
    if azul_detectado:
        device.suck(True)
    else:
        device.suck(False)

    cv2.imshow('frame', frame)
    cv2.imshow('framehsv', hsvframe)

    if cv2.waitKey(27) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
device.close()
