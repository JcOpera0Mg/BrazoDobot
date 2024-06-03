from serial.tools import list_ports
import pydobot
from color import *
import cv2
import numpy as np
available_ports = list_ports.comports()
print(f'available ports: {[x.device for x in available_ports]}')
port = available_ports[2].device

device = pydobot.Dobot(port=port, verbose=True)

(x, y, z, r, j1, j2, j3, j4) = device.pose()
print(f'x:{x} y:{y} z:{z} j1:{j1} j2:{j2} j3:{j3} j4:{j4}')

# Número de pasos para un giro completo (360 grados)
num_steps = 360
# Incremento de ángulo en cada paso
step_angle = 1

#pos 0: x:300, y:0, z:90, r:0
#x: [187.8 -  313.4] 100  300
#y: [-96.4 - 97.3]  -90   90
#z: [-102.7 - 120.7] -95  110




# j1:[-114 - 125.1] lateral
# j2:[-5.1 - 67] columna
# j3:[-15 - 64.9] antebrazo
# j1: 0 j2:-2.3 j3:7.9 j4:0

# for _ in range(num_steps):
#     device.move_to(x, y-90, z, r,wait=True)
#     device.wait(100)  
#     device.move_to(x, y+90, z, r,wait=True)
#     device.move_to()
#     device.wait(100) 
# device.close()
print("valor j1:",j1)
print("valor j2:",j2)
print("valor j3:",j3)
print("valor j4:",j4)
# device.move_to(j1, j2+20, j3, j4,wait=True)
# device.wait(100) 
# j2 = j2 + 20
def Pos_Inicial():
    j1 = 0
    j2 = 15 
    j3 = 0
    device.move_to(j1, j2, j3, j4,wait=True)
    device.wait(100)
    # device.suck(False)
    return j1,j2,j3
# j1 += 50
# device.move_to(j1, j2, j3, j4,wait=True)
# device.wait(100)
# j1 += 50
# device.move_to(j1, j2, j3, j4,wait=True)
# device.wait(100)
# Pos_Inicial() 

# j2 += 30
# device.move_to(j1, j2, j3, j4,wait=True)
# device.wait(100)
# j3 += 60
# device.move_to(j1, j2, j3, j4,wait=True)
# device.wait(100)
# Pos_Inicial()
# device.suck(False)
# j1 = 0
# j2 = 15 
# j3 = 0
# device.move_to(j1, j2, j3, j4,wait=True)
# device.wait(100)
j1,j2,j3 = Pos_Inicial()
cap = cv2.VideoCapture(0)#('highway.mp4')
#frame = cv2.imread('cuborojo.jpg')
#cap = cv2.VideoCapture(0)
rojo_detecto = False
azul_detecto = False
bucle = True

for _ in range(num_steps): 
# while True:
    j1,j2,j3 = Pos_Inicial()
    _ , frame =  cap.read()
    #_ , frame = cap.read()
    hsvframe = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
    while True:
        _ , frame =  cap.read()
        #_ , frame = cap.read()
        hsvframe = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
        cv2.imshow('frame',frame)
        cv2.imshow('framehsv',hsvframe)
        if cv2.waitKey(27) == ord('q'):
            device.suck(False)
            #device._set_end_effector_suckper(False)
            break
        if cv2.waitKey(27) == ord('w'):
            azul_detecto,x,y,z,h = detectColor(frame,hsvframe,[94,80,2],[120,255,255],[255,0,0],"azul")
            if azul_detecto and x!=0 and y!=0:
                break
            #device._set_end_effector_suckper(False)

        
    print("valor x:",x)
    print("valor y:",y)
    print("valor z:",z)
    print("valor h:",h)
    rojo_detecto,x,y,z,h = detectColor(frame,hsvframe,[136,87,111],[180,255,255],[0,0,255],"rojo")
    if rojo_detecto == False:
        azul_detecto,x,y,z,h = detectColor(frame,hsvframe,[94,80,2],[120,255,255],[255,0,0],"azul")
    # Pos_Inicial()
    #j1 = j1 + 50
    # device.move_to(j1, j2, j3, j4,wait=True)
    # device.wait(100)
    x -=20
    y -=20
    j1 = 3.5
    j1 = j1 + (x/11.55)
    device.move_to(j1, j2, j3, j4,wait=True)
    device.wait(100)
    j2 = 46.3
    j3 = 70.5
    print("y/10",y/10)
    j2 = j2 + ((y/6.5))
    j3 = j3 - (((y/6.5)*1.22)) 
    if x>100:
        j2 += 4
        j3 -= 4
    if(x>200):
        j2 +=5
        j3 -=5
    if(x>300):
        j2+=5
        j3 -=5
    # if x > 100:
    #     j3 = j3 + 2
    #     j2 = j2 + 3
    # else:
    #     j3 = j3 + 5.9
    # if y > 70:
    #     j2 = j2 + 4
    device.move_to(j1, j2, j3, j4,wait=True)
    print("valor j1:",j1)
    print("valor j2:",j2)
    print("valor j3:",j3)
    device.wait(100)
    # print("valor j1:",j1)
    # print("valor j2:",j2)
    # print("valor j3:",j3)
    # print("valor j4:",j4)
    # device.suck(True)
    if azul_detecto:
        print('detecto azul')
        device.suck(True)
        device.wait(200)
        #device.suck(True)
    if rojo_detecto:
        print('detecto rojo')
        device.suck(True)
        #device.suck(True)
    if rojo_detecto == False and azul_detecto == False:
        device.suck(False)
        #device.suck(False)   
    
    device.wait(100)
    j1,j2,j3 = Pos_Inicial()
    
    #j1 = j1 - 50
    # device.move_to(j1, j2, j3, j4,wait=True)
    # device.wait(100)
    j1 += 55
    j2 = j2 + 30
    j3 = j3 + 40 
    device.move_to(j1, j2, j3, j4,wait=True)
    cv2.imshow('frame',frame)
    cv2.imshow('framehsv',hsvframe)
    if cv2.waitKey(27) == ord('q'):
        device.suck(False)
        #device._set_end_effector_suckper(False)
        break
    device.wait(100)
    device.suck(False)
    device.wait(300)
    #device.suck(False)
    # print("valor j1:",j1)
    # print("valor j2:",j2)
    # print("valor j3:",j3)
    # print("valor j4:",j4)
    j1,j2,j3 = Pos_Inicial()
    
    
    #cv2.imshow('blue_mask',res_blue)
 
 
device.close()