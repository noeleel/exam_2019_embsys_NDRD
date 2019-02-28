import socket
import sys
import getopt
from tkinter import *
from tkinter.ttk import *
from tkinter.messagebox import *
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


TAILLE_IMAGE =  40*480*3*8 #Taille du Buffer pour la recuperation




class GUI(Tk):
    def __init__(self,IP="192.168.1.20", port_serveur_servo = 9000, port_serveur_camera = 7000):
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

        self.Frame_1 = Frame(self, borderwidth=2,relief = GROOVE)
        self.Frame_2 = Frame(self, borderwidth=2,relief = GROOVE)

        self.Frame_1.pack(side = TOP)
        self.Frame_2.pack(side = LEFT)

        self.b_quit = Button(master=self.Frame_1, text="Quit", command=self._quit)
        self.b_quit.pack(side=BOTTOM)


        self.pos = Scale(self.Frame_1, from_=1, to=180,orient='horizontal')
        self.pos.pack()

        self.b_switch = Button(self.Frame_1,text="Capture",command=self.switch)
        self.b_switch.pack(side=BOTTOM)   

        self.label_cam = Label(self.Frame_2,text="Camera Status")
        self.label_servo = Label(self.Frame_2,text="Servo Status")

        self.led_cam = Label(self.Frame_2,text = "     " ,background = 'red')
        self.led_servo = Label(self.Frame_2,text = "     " ,background = 'red')

        self.label_cam.grid(column = 0, row = 0,columnspan = 2)
        self.label_servo.grid(column = 0, row = 1,columnspan = 2)

        self.led_cam.grid(column = 2, row = 0)
        self.led_servo.grid(column = 2, row = 1)
        
        blank = np.zeros((480,640))
        self.ax.imshow(blank,cmap = "gray")
        self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

        self.servo = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address_servo = (IP, port_serveur_servo)
        self.wait_servo_i=0
        self.wait_servo()
        

        self.cam = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address_cam = (IP, port_serveur_camera)
        self.wait_cam_i = 0
        self.wait_cam()
        self.runtime()

    def _quit(self):
        try:
            print("Quitting program")
            self.servo.send(bytes([0])) #envoie d'une commande pour indiquer au servo l'arrêt
        except :
            pass
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
        image = np.array(image[2:640*480+2]).reshape((480,640))#recuperation de l'image parmi les données envoyées
        self.ax.clear()
        self.ax.imshow(image,cmap='gray')
        self.canvas.draw()
        

    #Fonction pour attendre un connexion entre le camera et le servo
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
            self.led_servo["background"] = "lawn green"
            print("Connection Established with servomotor")
            syslog.syslog(syslog.LOG_INFO, 'Connection Established with servomotor')
        except:
            if self.servo_connected:
                self.led_servo["background"] = "red"
                self.servo_connected = 0
            if self.wait_servo_i>10:
                print("Time Out")
                syslog.syslog(syslog.LOG_ERR, "Time Out")
                #self._quit()
            else:
                self.wait_servo_i+=1
                self.after(10000,self.wait_servo)

    #Fonction pour attendre un connexion entre le camera et le client
    def wait_cam(self):
        if self.quit_info:
            self._quit()
        print("Try number ",self.wait_cam_i," for camera")
        self.cam.settimeout(None)
        try:
            self.cam.settimeout(10)
            self.cam.connect(self.server_address_cam)
            print('connecting to {} port {}'.format(*self.server_address_cam))
            self.cam.send(b"0")
            syslog.syslog(syslog.LOG_INFO, 'connecting to {} port {}'.format(*self.server_address_cam))
            self.wait_cam_i = 0
            self.camera_connected = 1
            self.led_cam["background"] = "lawn green"
            print("Connection Established with camera")
            syslog.syslog(syslog.LOG_INFO, 'Connection Established with camera')
        except Exception as e:
            print(e)
            if self.camera_connected:
                self.led_cam["background"] = "red"
                self.camera_connected = 0
            if self.wait_cam_i>10:
                print("Time Out")
                syslog.syslog(syslog.LOG_ERR, "Time Out")
                #self._quit()
            else:
                self.wait_cam_i+=1
                self.after(10000,self.wait_cam)
        

    def runtime(self):
        self.runtime_servo()#Fonction appelé toutes les secondes pour l'envoi de données au servomoteur
        self.runtime_camera()#Fonction appelé toutes les 40ms  pour l'envoi et la reception de données avec la caméra
    
    def runtime_servo(self):
        if self.servo_connected:
            position = int(self.pos.get())
            if position == 0:
                position = 1
            try:
                print(position)
                self.servo.send(bytes([position]))
            except:
                self.wait_servo()
        else:
            self.wait_servo()
        
        if self.quit_info:
            self._quit()

        self.after(5000,self.runtime_servo)

    def runtime_camera(self):
        if self.camera_connected:
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
        else:
            self.wait_cam()

        if self.quit_info:
            self._quit()

        self.after(40,self.runtime_camera)

    #Gere les différents signaux et met la varaiable self.quit_info à true pour arréter proprement le programme
    def signal_handler(self,sig, frame):
        if (sig==signal.SIGINT or sig==signal.SIGTSTP or sig==sig.SIGTERM):
            self.quit_info = 1
            syslog.syslog(syslog.LOG_ERR, "SIGINT signal received")

    #Permet de lancer ou d'arreter la capture
    def switch(self):
        if self.capture:
            self.capture = 0
            self.b_switch["text"]="Capture"
        else:
            self.capture = 1
            self.b_switch["text"]="Stop"



if __name__ == "__main__":
    print("Launching " + sys.argv[0])
    IP = "192.168.1.20"
    port_camera = 7000
    port_servomoteur = 9000
    syslog.syslog(syslog.LOG_INFO, "Launching " + sys.argv[0] + "\n")
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h:i:s:c", ["help=", "ip=", "port_servomoteur=", "port_camera="])
    except getopt.GetoptError as err:
        print(err)
        print("\n")
        print("Wrong arguments or Not enough arguments")
        print("Usage :")
        print("Servomotor_servo -i ip -s port_servomoteur -c port_camera")
        print(" or ")
        print("Servomotor_servo -ip ip -port_servomoteur port_servomoteur -port_camera port_camera")
        print("Quitting the program!")
        syslog.syslog(syslog.LOG_ERR, "Quitting the program!\n")
        sys.exit(2)
    print(opts)
    for o, a in opts:
        if o in ("-h", "--help"):
            print("Options and arguments : ")
            print("-h or --help             | Display this help message")
            print("-i or --ip               | Default is localhost. Ip Address of the RPi on which the server is running. ")
            print("-s or --port_servomoteur | Default is 9000. Port of the RPi on which the server managing the servomotor is running ")
            print("-c or --port_camera      | Default is 7000. Port of the RPi on which the server managing the camera is running")
            print("\n")
            print("Usage :")
            print("Servomotor_servo -i ip -s port_servomoteur -c port_camera")
            print(" or ")
            print("Servomotor_servo -ip ip -port_servomoteur port_servomoteur -port_camera port_camera")
            print("Quitting the program!")
            syslog.syslog(syslog.LOG_ERR, "Quitting the program!\n")
            sys.exit()
        elif o in ("-i", "--ip"):
            IP = a
        elif o in ("-s", "--port_servomoteur"):
            port_servomoteur = int(a)
        elif o in ("-c", "--port_camera"):
            port_camera = int(a)
        else:
            assert False, "unhandled option"
            print("Quitting the program!")
            syslog.syslog(syslog.LOG_ERR, "Quitting the program!\n")
            sys.exit(1)

    interface = GUI(IP, port_servomoteur, port_camera)
    signal.signal(signal.SIGINT, interface.signal_handler)
    signal.signal(signal.SIGTSTP, interface.signal_handler)
    signal.signal(signal.SIGTERM, interface.signal_handler)
    interface.mainloop()