import cv2
import numpy as np
from serial.tools import list_ports
import pydobot

def get_available_ports():
    available_ports = list_ports.comports()
    return [x.device for x in available_ports]

def initialize_dobot(port):
    return pydobot.Dobot(port=port, verbose=True)

def get_pose(device):
    return device.pose()

def move_to_initial_position(device):
    j1, j2, j3, j4 = 0, 15, 0, 0
    device.move_to(j1, j2, j3, j4, wait=True)
    device.wait(100)
    return j1, j2, j3

def detect_color(frame, hsv_frame, lower, upper, color, text):
    mask = cv2.inRange(hsv_frame, lower, upper)
    mask = cv2.dilate(mask, None, iterations=2)
    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cont in contours:
        area = cv2.contourArea(cont)
        if area > 100:
            x, y, w, h = cv2.boundingRect(cont)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, text, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 2, color)
            return True, x, y, w, h

    return False, 0, 0, 0, 0

def main():
    available_ports = get_available_ports()
    if len(available_ports) < 3:
        print(f'Available ports: {available_ports}')
        return
    
    port = available_ports[2]
    device = initialize_dobot(port)
    
    j1, j2, j3, j4 = get_pose(device)
    print(f'x:{j1} y:{j2} z:{j3} r:{j4}')
    
    j1, j2, j3 = move_to_initial_position(device)
    
    cap = cv2.VideoCapture(0)
    num_steps = 360

    for _ in range(num_steps):
        j1, j2, j3 = move_to_initial_position(device)
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            cv2.imshow('Frame', frame)
            cv2.imshow('HSV Frame', hsv_frame)
            
            if cv2.waitKey(27) == ord('q'):
                device.suck(False)
                break

            lower_blue = np.array([94, 80, 2])
            upper_blue = np.array([120, 255, 255])
            azul_detected, x, y, z, h = detect_color(frame, hsv_frame, lower_blue, upper_blue, (255, 0, 0), "Azul")
            
            if azul_detected and x != 0 and y != 0:
                break
        
        if not azul_detected:
            continue
        
        mover = x
        j1 += mover / 12
        device.move_to(j1, j2, j3, j4, wait=True)
        device.wait(100)
        
        j2 += 45
        j3 += 53
        mover = y
        j2 += min(mover / 1.5, 5)
        j3 -= mover / 4
        device.move_to(j1, j2, j3, j4, wait=True)
        
        cv2.imshow('Frame', frame)
        cv2.imshow('HSV Frame', hsv_frame)
        
        if cv2.waitKey(27) == ord('q'):
            device.suck(False)
            break

        device.suck(True)
        device.wait(100)
        
        j1, j2, j3 = move_to_initial_position(device)
        j1 -= 50
        j2 += 45
        j3 += 53
        device.move_to(j1, j2, j3, j4, wait=True)
        
        cv2.imshow('Frame', frame)
        cv2.imshow('HSV Frame', hsv_frame)
        
        if cv2.waitKey(27) == ord('q'):
            device.suck(False)
            break

        device.suck(False)
        j1, j2, j3 = move_to_initial_position(device)
    
    cap.release()
    cv2.destroyAllWindows()
    device.close()

if __name__ == "__main__":
    main()
