import socket
import sys
import signal
#import RPi.GPIO as GPIO
import time
import datetime

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

class Servomotor_server():
    def __init__(self, host = "localhost", port = 9000, buffer_size = 1024, timeout = 10):
        self.hostname = host
        self.port = port
        self.buffer_size = buffer_size
        self.timeout = timeout
        self.IS_TIMEOUT = False
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(timeout)
        self.conn = None
        self.addr = None
        

    def __str__(self):
        string = ""
        string += (" Serveur Servomoteur is up \n")
        string += ("\nServeur hostname : " + str(self.hostname))
        string += ("\nServeur port : " + str(self.port))
        string += ("\n")
        return string 

    def launch(self):
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(0)
        
    def connect(self):
        self.conn, self.addr = self.socket.accept()
        print("{} connected".format(self.addr))

    def end_connexion(self):
        self.conn.close()
        self.socket.close()
        print("The connexion has been closed. \n")
    
    def control_servomotor(self, angle):
        pwm.start(0)
        duty = angle / 18 + 2
        GPIO.output(3, True)
        pwm.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(3, False)
        pwm.ChangeDutyCycle(0) 
        pwm.stop()
        GPIO.cleanup()

    def timeout(self):
        if self.IS_TIMEOUT == True:
            self.end_connexion()

    def signal_handler(self,signum, frame):
        if signum == signal.SIGINT:
            self.end_connexion()
            print(" Servomotor Server Process has been killed! \n")
        elif signum == signal.SIGTERM:
            self.end_connexion()
            print(" Servomotor Server Process has been terminated! \n")

if __name__ == "__main__":
    print("Launching " + sys.argv[0])

    ## Checking user arguments ##
    if len(sys.argv) < 2:
        print("Not enough arguments \n")
        print("Usage : Servomotor_server gpio_pin hostname port image_buffer_size timeout\n")
        print("Quitting the program!\n")
        sys.exit(0)
    if len(sys.argv) > 1:
        if len(sys.argv) == 2:
            gpio_pin = sys.argv[1]
            Server = Servomotor_server()
        elif len(sys.argv) == 3:
            gpio_pin = sys.argv[1]
            host = sys.argv[2]
            Server = Servomotor_server(host)
        elif len(sys.argv) == 4:
            gpio_pin = sys.argv[1]
            host = sys.argv[2]
            port = sys.argv[3]
            Server = Servomotor_server(host, port)
        elif len(sys.argv) == 5:
            gpio_pin = sys.argv[1]
            host = sys.argv[2]
            port = sys.argv[3]
            buffer_size = sys.argv[4]
            Server = Servomotor_server(host, port, buffer_size)
        elif len(sys.argv) == 6:
            gpio_pin = sys.argv[1]
            host = sys.argv[2]
            port = sys.argv[3]
            buffer_size = sys.argv[4]
            timeout = sys.argv[5]
            Server = Servomotor_server(host, port, buffer_size, timeout)


    ## Setting GPIO and PWM up ##
    #GPIO.setmode(GPIO.BOARD)
    #GPIO.setup(gpio_pin, GPIO.OUT)
    #pwm=GPIO.PWM(gpio_pin, 50)
    #GPIO.setwarnings(False)

    ## Launching the server ##
    print(Server)

    ## Initializing the signal handler ##
    signal.signal(signal.SIGINT, Server.signal_handler)
    signal.signal(signal.SIGTSTP, Server.signal_handler)
    signal.signal(signal.SIGTERM, Server.signal_handler)

    ## Connecting to the client ##
    Server.launch()
    while Server.conn == None:
        Server.connect()

    ## Listening to the client ##
    while True:
        ts = time.time()
        st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        try:
            # Receive command
            data = Server.conn.recv(Server.buffer_size)
            angle = bytes_to_int(data)
            if angle == 0 :
                print("[ {} - {} ] Value 0 has been received. Stopping the communication.\n".format(st, Server.addr))
                print("[ {} - {} ] Client disconnected from server \n".format(st, Server.addr))
                print("[ {} - {} ] Closing the server\n".format(st, Server.addr))
                Server.end_connexion()
                break
            if angle <0 or angle > 180:
                print("[ {} - {} ] Wrong value for angle : {} \n".format(st, Server.addr, angle))
            else:
                # Move the servomotor
                #Server.control_servomotor()
                print("[ {} - {} ] Value send is {} \n".format(st, Server.addr, angle))
        except socket.timeout:
            print("[ {} - {} ] Client disconnected from server \n".format(st, Server.addr))
            print("[ {} - {} ] Closing the server\n".format(st, Server.addr))
            Server.timeout()
            sys.exit(0)
