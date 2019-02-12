import socket
import sys
import tkinter as tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.pyplot import imshow
import signal


TAILLE_IMAGE = 1


class GUI(tk.Tk):
    def __init__(self,IP="localhost:9000"):
        super().__init__()
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.data=[]
        self.quit_info = 0
        self.capture = 0 
        self.servo_connected = 0
        self.camera_connected = 0
        self.b_quit = tk.Button(master=self, text="Quit", command=self._quit)
        self.b_quit.pack(side=tk.BOTTOM)

        self.pos = tk.Scale(self, from_=0, to=180,orient='horizontal')
        self.pos.pack()

        self.b_switch = tk.Button(self,text="Capture",command=self.switch)
        self.b_switch.pack(side=tk.BOTTOM)        


        self.servo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address_servo = (IP, 10)
        self.wait_servo_i=0
        self.wait_servo()

        self.cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address_cam = (IP, 11)
        self.wait_cam_i = 0
        self.wait_cam()
        self.runtime()

    def _quit(self):
        self.servo.close()
        self.cam.close()
        self.quit()     
        self.destroy()  
    
    def image(self):
        self.ax.clear()
        self.ax.imshow(self.data)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)


    def wait_servo(self):
        if self.quit_info:
            self._quit()
        print("Try number ",self.wait_servo_i," for servo")
        self.servo.settimeout(None)
        try:
            self.servo.settimeout(1)
            self.servo.connect(self.server_address_servo)
            print('connecting to {} port {}'.format(*self.server_address_servo))
            self.wait_servo_i = 0 
            self.servo_connected = 1 
        except:
            if self.servo_connected:
                self.server_connected = 0
            if self.wait_servo_i>5:
                print("Time Out")
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
            self.cam.connect(self.server_address_Cam)
            print('connecting to {} port {}'.format(*self.server_address_cam))
            self.wait_cam_i = 0
            self.camera_connected = 1 
        except:
            if self.camera_connected:
                self.camera_connected = 0
            if self.wait_cam_i>5:
                print("Time Out")
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
                self.cam.send(bytes([self.capture]))
            except :
                self.wait_cam()
            self.data = self.cam.recv(TAILLE_IMAGE)
            if len(self.data)==TAILLE_IMAGE :
                self.image()
            
        if self.quit_info:
            self._quit()

        self.after(10,self.runtime)

    def signal_handler(self,sig, frame):
        if (sig==signal.SIGINT):
            self.quit_info = 1

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

