#!/usr/bin/python3
import socket
import os, re

def check_detection_process():
    popen = os.popen("ps -aux | grep detectionAPP | awk '{print $2 , $11}'")
    ps_result = popen.read()
    ps_result = ps_result.split('\n')

    detection_process_on = False
    detection_process_pid = ''
    for process in ps_result:
        try:
            pid, p_name = process.split(' ')
            if p_name == '/home/pi/Projects/pyenv/ML/bin/python':
                detection_process_on = True
                detection_process_pid = pid
        except:
            pass

    return detection_process_on, detection_process_pid

def turn_on_camera():
    camera_status = os.system("sudo /home/pi/Projects/py/ML/tensorflow/models/detectionAPP_v0.sh &")
    return camera_status



service_port = ('0.0.0.0', 9000)

serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serv.bind(service_port)
print('socket established with {}'.format(service_port))

serv.listen()
print('Start listening')


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
            detection_process_on, detection_process_pid = check_detection_process()
            if detection_process_on == True:
                res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"camera is already 'ON', no need to restart"
            else:
                camera_status = turn_on_camera()
                if camera_status == 0:
                    res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"camera turned on"
                else:
                    res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"fail to turn camera on"
            res = res.encode('utf-8')
            conn.send(res)
            break

        elif len(re.findall('GET /', data))>0 and len(re.findall('camera_off', data))>0:
            detection_process_on, detection_process_pid = check_detection_process()
            if detection_process_on == False:
                res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"camera is already 'OFF', no process needed"
            else:
                camera_status = os.system('sudo kill {}'.format(detection_process_pid))
                if camera_status == 0:
                    res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"camera turned off"
                else:
                    res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"fail to turn camera off"                
            res = res.encode('utf-8')
            conn.send(res)
            break

        else:
            res = "HTTP/1.1 200 OK\n"+"Content-Type: text/html\n"+"\n"+"Argument incorrect: 1. Only support http 'GET'\n2.Either 'camera_on' or 'camera_off' "
            res = res.encode('utf-8')
            conn.send(res)
            break

    conn.close()
    print('Client disconnected')