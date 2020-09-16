#!/usr/bin/python3
import socket
import os, re, time, threading
from detectionAPP_v1_noCAM import DetetionAPP 

model_dir = '/home/pi/Projects/py/ML/tensorflow/models'
cam_stop = False

def cam_init():
    global cam_stop
    frameGen = detetionAPP.camera_cap()
    while True:
        frame = frameGen.__next__()
        if cam_stop == True:
            break

service_port = ('0.0.0.0', 9003)

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serv.bind(service_port)
print('socket established with {}'.format(service_port))

serv.listen()
print('Start listening')

detetionAPP = DetetionAPP(model_dir)

while True:
    conn, addr = serv.accept()
    print('Client from', addr)

    while True:
        data = conn.recv(1024)
        data = data.decode('utf-8')
        print('Recieve data from client: ', data)

        if not data or data == '':
            break

        elif len(re.findall('GET /', data))>0 and len(re.findall('camera_on', data))>0:

            if detetionAPP.cam_status == True:
                res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"camera is already 'ON', no need to restart"
            else:
                # Try Turn camera capture on (time.sleep depands on capture speed)
                
                try:
                    cam_thread = threading.Thread(target=cam_init)
                    cam_stop = False
                    cam_thread.start()
                    time.sleep(10) # this value depands, too small might casue mistaken respone of 'fail to turn camera on'
                except:
                    print('Error: Repeatly processing camera capture')

                if detetionAPP.cam_status == True:
                    res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"camera turned on"
                else:
                    res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"fail to turn camera on"

            res = res.encode('utf-8')
            conn.send(res)
            break

        elif len(re.findall('GET /', data))>0 and len(re.findall('camera_off', data))>0:

            cam_stop = True
            res = res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"Try to turn camera off" 
            print(res)              
            res = res.encode('utf-8')
            conn.send(res)
            detetionAPP.cam_status = False
            break

        else:
            res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"Argument incorrect: 1. Only support http 'GET'\n2.Either 'camera_on' or 'camera_off' "
            res = res.encode('utf-8')
            conn.send(res)
            break
    
    conn.close()
    print('Client disconnected')
    
    