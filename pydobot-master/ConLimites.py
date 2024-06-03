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
 
def Pos_Inicial(): 
    j1 = 0 
    j2 = 15  
    j3 = 0 
    device.move_to(j1, j2, j3, j4, wait=True) 
    device.wait(100) 
    return j1, j2, j3 
 
def verificar_limites(j1, j2, j3): 
    j1 = max(LIMITS['j1'][0], min(LIMITS['j1'][1], j1)) 
    j2 = max(LIMITS['j2'][0], min(LIMITS['j2'][1], j2)) 
    j3 = max(LIMITS['j3'][0], min(LIMITS['j3'][1], j3)) 
    return j1, j2, j3 
 
rojo_detecto = False 
azul_detecto = False 
num_steps = 360 
 
for _ in range(num_steps): 
    j1, j2, j3 = Pos_Inicial() 
     
    # Capturar un frame de la cámara 
    _, frame = cap.read() 
    hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
     
    while True: 
        _, frame = cap.read() 
        hsvframe = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV) 
        cv2.imshow('frame', frame) 
        cv2.imshow('framehsv', hsvframe) 
         
        if cv2.waitKey(27) == ord('q'): 
            device.suck(False) 
            break 
         
        azul_detecto, xc, yc, z, h = detectColor(frame, hsvframe, [94,80,2], [120,255,255], [255,0,0], "azul") 
        if azul_detecto and xc != 0 and yc != 0: 
            break 
     
    print(f"Valor x (cámara): {xc}, Valor y (cámara): {yc}, Valor z: {z}, Valor h: {h}") 
     
    # Transformar las coordenadas de la cámara a las coordenadas del brazo 
    xb, yb = transformar_coordenadas(xc, yc) 
    print(f"Valor x (brazo): {xb}, Valor y (brazo): {yb}") 
     
    rojo_detecto, xc, yc, z, h = detectColor(frame, hsvframe, [136,87,111], [180,255,255], [0,0,255], "rojo") 
    if not rojo_detecto: 
        azul_detecto, xc, yc, z, h = detectColor(frame, hsvframe, [94,80,2], [120,255,255], [255,0,0], "azul") 
     
    # Calcular las posiciones del brazo basadas en la detección 
    j1 += (xb / 12) 
    j2 += (yb / 1.5) 
     
    # Verificar y ajustar los límites 
    j1, j2, j3 = verificar_limites(j1, j2, j3) 
     
    device.move_to(j1, j2, j3, j4, wait=True) 
    device.wait(100) 
     
    j2 += 45 
    j3 += 53 
     
    # Verificar y ajustar los límites antes de mover 
    j1, j2, j3 = verificar_limites(j1, j2, j3) 
    device.move_to(j1, j2, j3, j4, wait=True) 
     
    cv2.imshow('frame', frame) 
    cv2.imshow('framehsv', hsvframe) 
     
    if cv2.waitKey(27) == ord('q'): 
        device.suck(False) 
        break 
     
    device.wait(100) 
     
    if azul_detecto: 
        print('Detecto azul') 
        device.suck(True) 
    if rojo_detecto: 
        print('Detecto rojo') 
        device.suck(True) 
    if not rojo_detecto and not azul_detecto: 
        device.suck(False) 
     
    device.wait(100) 
    j1, j2, j3 = Pos_Inicial() 
    j1 -= 50 
    j2 += 45 
    j3 += 53 
     
    # Verificar y ajustar los límites antes de mover 
    j1, j2, j3 = verificar_limites(j1, j2, j3) 
    device.move_to(j1, j2, j3, j4, wait=True) 
     
    cv2.imshow('frame', frame) 
    cv2.imshow('framehsv', hsvframe) 
     
    if cv2.waitKey(27) == ord('q'): 
        device.suck(False) 
        break 
     
    device.wait(100) 
    device.suck(False) 
    j1, j2, j3 = Pos_Inicial() 
 
device.close()