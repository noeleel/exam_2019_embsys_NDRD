import socket
import sys
import tkinter as tk
import matplotlib
matplotlib.use("Agg")
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.pyplot import imshow,figure
import numpy as np
import matplotlib.pyplot as plt
import signal
import syslog
syslog.openlog("Client_Servomotor_Camera")
print("Message are logged in /var/log/syslog")


TAILLE_IMAGE =  40*480*3*8




class GUI(tk.Tk):
    def __init__(self,IP="localhost"):
        super().__init__()
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.data=[]
        self.quit_info = 0
        self.capture = 0 
        self.servo_connected = 0
        self.camera_connected = 0
        self.receiving = 0
        self.b_quit = tk.Button(master=self, text="Quit", command=self._quit)
        self.b_quit.pack(side=tk.BOTTOM)

        self.pos = tk.Scale(self, from_=1, to=180,orient='horizontal')
        self.pos.pack()

        self.b_switch = tk.Button(self,text="Capture",command=self.switch)
        self.b_switch.pack(side=tk.BOTTOM)        


        self.servo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address_servo = (IP, 9000)
        self.wait_servo_i=0
        self.wait_servo()
        


        self.cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address_cam = (IP, 8080)
        self.wait_cam_i = 0
        self.wait_cam()
        self.runtime()

    def _quit(self):
        self.servo.send(bytes([0]))
        self.servo.close()
        self.cam.close()
        self.quit()     
        self.destroy()  
    
    def image(self):
        image = []
        number = 0
        
        for i in range(len(self.image_recupe)):
            if self.image_recupe[i]!=59:
                number = number *10 + int(self.image_recupe[i]-48)
            else:
                image.append(number)
                number = 0
        image_red = np.array(image[2:640*480+2]).reshape((480,640))
        image = np.zeros((480,640,3))
        image[:,:,0] = image_red
        self.ax.clear()
        self.ax.imshow(image_red,cmap='gray')
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


    def wait_servo(self):
        if self.quit_info:
            self._quit()
        print("Try number ",self.wait_servo_i," for servo")
        self.servo.settimeout(20)
        try:
            self.servo.settimeout(10)
            self.servo.connect(self.server_address_servo)
            print('connecting to {} port {}'.format(*self.server_address_servo))
            syslog.syslog(syslog.LOG_INFO, 'connecting to {} port {}'.format(*self.server_address_servo))
            self.wait_servo_i = 0 
            self.servo_connected = 1
            print("Connection Established with servomotor")
            syslog.syslog(syslog.LOG_INFO, 'Connection Established with servomotor')
        except:
            if self.servo_connected:
                self.server_connected = 0
            if self.wait_servo_i>5:
                print("Time Out")
                syslog.syslog(syslog.LOG_ERR, "Time Out")
                self._quit()
            else:
                self.wait_servo_i+=1
                self.after(1000,self.wait_servo)


    def wait_cam(self):
        if self.quit_info:
            self._quit()
        print("Try number ",self.wait_cam_i," for camera")
        self.cam.settimeout(None)
        try:
            self.cam.settimeout(1)
            self.cam.connect(self.server_address_cam)
            print('connecting to {} port {}'.format(*self.server_address_cam))
            self.cam.send(b"0")
            syslog.syslog(syslog.LOG_INFO, 'connecting to {} port {}'.format(*self.server_address_cam))
            self.wait_cam_i = 0
            self.camera_connected = 1
            print("Connection Established with camera")
            syslog.syslog(syslog.LOG_INFO, 'Connection Established with camera')
        except Exception as e:
            print(e)
            if self.camera_connected:
                self.camera_connected = 0
            if self.wait_cam_i>5:
                print("Time Out")
                syslog.syslog(syslog.LOG_ERR, "Time Out")
                self._quit()
            else:
                self.wait_cam_i+=1
                self.after(1000,self.wait_cam)
        

    def runtime(self):
        if self.servo_connected and self.camera_connected:
            position = self.pos.get()

            try:
                self.servo.send(bytes([position]))
            except:
                self.wait_servo()

            try:
                if not self.capture or self.receiving:
                    self.cam.send(b"0")
                else:
                    self.cam.send(b"1")
            except :
                self.wait_cam()

            self.data = self.cam.recv(TAILLE_IMAGE)
            if self.data != b'empty' and not self.receiving:
                self.receiving = 1
                self.image_recupe = np.array([])

            if self.data==b'empty':
                if self.receiving:
                    self.image()
                self.receiving = 0

            if self.receiving:
                temp = np.array([self.data[i] for i in range(len(self.data))])
                self.image_recupe = np.concatenate((self.image_recupe,temp))
            
        if self.quit_info:
            self._quit()

        self.after(40,self.runtime)

    def signal_handler(self,sig, frame):
        if (sig==signal.SIGINT):
            self.quit_info = 1
            syslog.syslog(syslog.LOG_ERR, "SIGINT signal received")

    def switch(self):
        if self.capture:
            self.capture = 0
            self.b_switch["text"]="Capture"
        else:
            self.capture = 1
            self.b_switch["text"]="Stop"



if __name__ == "__main__":
    IP = sys.argv[1]
    interface = GUI(IP)
    signal.signal(signal.SIGINT, interface.signal_handler)
    signal.signal(signal.SIGTSTP, interface.signal_handler)
    signal.signal(signal.SIGTERM, interface.signal_handler)
    interface.mainloop()

