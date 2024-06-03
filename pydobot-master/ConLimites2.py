from serial.tools import list_ports 
import pydobot 
from color import * 
import cv2 
import numpy as np 

# Inicializar cámara y dispositivo Dobot 
available_ports = list_ports.comports() 
print(f'available ports: {[x.device for x in available_ports]}') 
port = available_ports[2].device 

device = pydobot.Dobot(port=port, verbose=True) 
cap = cv2.VideoCapture(0) 

# Obtener y mostrar la posición inicial del robot 
(x, y, z, r, j1, j2, j3, j4) = device.pose() 
print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}') 

# Límites de los ángulos de las articulaciones 
LIMITS = { 
    'j1': (-114, 125.1), 
    'j2': (-5.1, 67), 
    'j3': (-15, 64.9) 
} 

# Función de calibración (ejemplo de valores de calibración) 
a1, b1 = 0.1, -15  # Parámetros de calibración para x 
a2, b2 = 0.1, -15  # Parámetros de calibración para y 

def transformar_coordenadas(xc, yc): 
    xb = a1 * xc + b1 
    yb = a2 * yc + b2 
    return xb, yb 

def verificar_limites(j1, j2, j3): 
    j1 = max(LIMITS['j1'][0], min(LIMITS['j1'][1], j1)) 
    j2 = max(LIMITS['j2'][0], min(LIMITS['j2'][1], j2)) 
    j3 = max(LIMITS['j3'][0], min(LIMITS['j3'][1], j3)) 
    return j1, j2, j3 

# Mover el brazo automáticamente para capturar coordenadas según la perspectiva de la cámara
def mover_brazo_para_calibracion():
    # Definir movimientos automáticos del brazo
    movimientos_brazo = [
        (200, 0, 50), (200, -50, 50), (200, 50, 50),
        (250, 0, 50), (250, -50, 50), (250, 50, 50),
        (300, 0, 50), (300, -50, 50), (300, 50, 50)
    ]
    coordenadas_capturadas = []

    for movimiento in movimientos_brazo:
        device.move_to(*movimiento, wait=True)
        device.wait(500)
        _, frame = cap.read()
        x, y, _, _ = device.pose()[:4]
        coordenadas_capturadas.append((x, y))

    return coordenadas_capturadas

# Posicionar el brazo inicialmente para capturar coordenadas
coordenadas_capturadas = mover_brazo_para_calibracion()

# Calcular matriz de transformación para la calibración
def calibrar_transformacion(coordenadas_camara, coordenadas_brazo):
    coordenadas_camara = np.float32(coordenadas_camara[:3])
    coordenadas_brazo = np.float32(coordenadas_brazo[:3])
    M = cv2.getAffineTransform(coordenadas_camara, coordenadas_brazo)
    return M

# Realizar calibración
M = calibrar_transformacion(coordenadas_capturadas, [
    (200, 0), (200, -50), (200, 50),
    (250, 0), (250, -50), (250, 50),
    (300, 0), (300, -50), (300, 50)
])

# Posicionar el brazo inicialmente
def posicionar_brazo_inicial():
    j1 = 0 
    j2 = 15  
    j3 = 0 
    device.move_to(j1, j2, j3, j4, wait=True) 
    device.wait(100) 
    return j1, j2, j3 

# Bucle principal
while True: 
    _, frame = cap.read() 
    hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 

    # Detección de color y movimiento del brazo
    azul_detectado, xc, yc, z, h = detectColor(frame, hsvframe, [94, 80, 2], [120, 255, 255], [255, 0, 0], "azul") 

    if azul_detectado and xc != 0 and yc != 0: 
        xb, yb = transformar_coordenadas(xc, yc) 
        print(f"Valor x (cámara): {xc}, Valor y (cámara): {yc}, Valor z: {z}, Valor h: {h}") 
        print(f"Valor x (brazo): {xb}, Valor y (brazo): {yb}") 

        j1 += (xb / 12) 
        j2 += (yb / 1.5) 

        j1, j2, j3 = verificar_limites(j1, j2, j3) 

        device.move_to(j1, j2, j3, j4, wait=True) 
        device.wait(100) 

        if azul_detectado: 
            print('Detecto azul') 
            device.suck(True) 
        else: 
            device.suck(False) 

        device.wait(100) 

        j1, j2, j3 = posicionar_brazo_inicial() 

    cv2.imshow('frame', frame) 
    cv2.imshow('framehsv', hsvframe) 

    if cv2.waitKey(1) == ord('q'): 
        device.suck(False) 
        break 

cap.release() 
cv2.destroyAllWindows() 
device.close()
