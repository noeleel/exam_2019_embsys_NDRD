import socket
import sys
import tkinter as tk
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.pyplot import imshow


TAILLE_IMAGE = 1


class GUI(tk.Tk):
    def __init__(self,IP):
        super().__init__()
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.data=[]
        
        self.b_quit = tk.Button(master=self, text="Quit", command=self._quit)
        self.b_quit.pack(side=tk.BOTTOM)

        self.pos = tk.Scale(self, from_=0, to=42,orient='horizontal')
        self.pos.pack()


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
        try:
            print('connecting to {} port {}'.format(*self.server_address_servo))
            self.servo.connect(self.server_address_servo)
            self.wait_servo_i = 0 
        except:
            if self.wait_servo_i>60:
                self._quit()
            else:
                self.wait_servo_i+=1
                self.after(1000,self.wait_servo)


    def wait_cam(self):
        try:
            print('connecting to {} port {}'.format(*self.server_address_cam))
            self.cam.connect(self.server_address_Cam)
            self.wait_cam_i = 0
        except:
            if self.wait_cam_i>60:
                self._quit()
            else:
                self.wait_cam_i+=1
                self.after(1000,self.wait_cam)


    def runtime(self):
        position = self.pos.get()
        try:
            self.servo.send(bytes([position]))
        except:
            self.wait.servo()

        try:
            self.cam.send(b' ')
        except :
            self.wait_cam()
        self.data = self.cam.recv(TAILLE_IMAGE)
        if len(self.data)==TAILLE_IMAGE :
            self.image()

        self.after(10,self.runtime)


if __name__ == "__main__":
    IP = sys.argv[1]
    a = GUI(IP)
    a.mainloop()
