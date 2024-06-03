import cv2
import numpy as np

def detectColor(frame,hsvframe,lower,upper,color,texto):
    #detectar color azul
    x = 0
    y = 0
    w = 0
    h = 0
    blue_lower = np.array(lower,np.uint8)
    blue_upper = np.array(upper,np.uint8)
    blue_mask = cv2.inRange(hsvframe,blue_lower,blue_upper)
    
    kernel = np.ones((5,5),"uint8")
    
    blue_mask = cv2.dilate(blue_mask,kernel)
    res_blue = cv2.bitwise_and(frame,frame,mask=blue_mask)
    contorno,h = cv2.findContours(blue_mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    for pic, cont in enumerate(contorno):
        area = cv2.contourArea(cont)
        if area > 300:
            x,y,w,h = cv2.boundingRect(cont)
            print ("x desde color: ",x)
            print ("y desde color: ",y)
            print ("w desde color: ",w)
            print ("h desde color: ",h)
            cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
            cv2.putText(frame,texto,(x,y),cv2.FONT_HERSHEY_SIMPLEX,2,color)
            
        return True,x,y,w,h # Color detectado
    return False,-1,-1,-1,-1  # Color no detectado
#cap = cv2.VideoCapture(0)#('highway.mp4')
# while True:
#     _ , frame = cap.read()
#     hsvframe = cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
#     # color red  136,87,111   180,255,255
#     # color verde 25,52,72    102,255,255    
#     #rojo
#     detectColor(frame,hsvframe,[136,87,111],[180,255,255],[0,0,255],"rojo")
#     #verde
#     #detectColor(frame,hsvframe,[25,52,72],[102,255,255],[0,255,0],"verde")
#     #azul
#     #detectColor(frame,hsvframe,[94,80,2],[120,255,255],[255,0,0],"azul")            
#     #amarillo
#     #detectColor(frame,hsvframe,[22,93,0],[45,255,255],[255,0,0],"amarillo")
                
#     cv2.imshow('frame',frame)
#     cv2.imshow('framehsv',hsvframe)
#     #cv2.imshow('blue_mask',res_blue)
#     if cv2.waitKey(27) == ord('q'):
#         break
# cap.release()
# cv2.destroyAllWindows()