import socket
import sys
import signal
import RPi.GPIO as GPIO
import time

def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

class Servomotor_server():
    def __init__(self, host = "localhost", port = 9000, buffer_size = 1024, timeout = 60):
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

    def connect(self):
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(0)
        self.conn, self.addr = self.socket.accept()

    def end_connexion(self):
        self.conn.close()
        self.socket.close()
        print("The connexion has been closed. \n")
    
    def receive_message(self):
        data = self.conn.recv(self.buffer_size)
        return data

    def control_servomotor(self, angle):
        pwm.start(0)
        duty = angle / 18 + 2
        GPIO.output(03, True)
        pwm.ChangeDutyCycle(duty)
        sleep(1)
        GPIO.output(03, False)
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
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(gpio_pin, GPIO.OUT)
    pwm=GPIO.PWM(gpio_pin, 50)
    GPIO.setwarnings(False)

    ## Launching the server ##
    print(Server)

    ## Initializing the signal handler ##
    signal.signal(signal.SIGINT, Server.signal_handler)
    signal.signal(signal.SIGTSTP, Server.signal_handler)
    signal.signal(signal.SIGTSTP, Server.signal_handler)

    ## Connecting to the client ##
    Server.connect()

    ## Listening to the client ##
    while not Server.IS_TIMEOUT:
        try:
            # Receive command
            data = Server.receive_message()
            angle = bytes_to_int(data)
            if angle <0 or angle > 180:
                print("Wrong value for angle : " + str(angle))
            else:
                # Move the servomotor
                Server.control_servomotor()
                print('pass')
        except socket.Timeouterror:
            print("Client disconnected from server \n")
            Server.timeout()
            sys.exit(0)

    Server.timeout()
    print("Closing the server\n")
    sys.exit(0)