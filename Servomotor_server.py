import socket
import sys
import getopt
import signal
#import RPi.GPIO as GPIO
import time
import datetime
import syslog
syslog.openlog("Server_Servomotor")
print("Message are logged in /var/log/syslog")
def bytes_to_int(bytes):
    result = 0
    for b in bytes:
        result = result * 256 + int(b)
    return result

class Servomotor_server():
    def __init__(self, host = "localhost", port = 9000, buffer_size = 1024, timeout = 300):
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
        syslog.syslog(syslog.LOG_INFO, string)
        return string 

    def launch(self):
        self.socket.bind((self.hostname, self.port))
        self.socket.listen(0)
        
    def connect(self):
        self.conn, self.addr = self.socket.accept()
        print("{} connected".format(self.addr))
        syslog.syslog(syslog.LOG_DEBUG, "{} connected".format(self.addr))

    def end_connexion(self):
        if not (self.conn is None):
            self.conn.close()
        self.socket.close()
        print("The connexion has been closed. \n")
        syslog.syslog(syslog.LOG_ALERT, "The connexion has been closed. \n")
    
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
            print("SIGINT signal raised!")
            print(" Servomotor Server Process has been killed! \n")
            syslog.syslog(syslog.LOG_ERR, " Servomotor Server Process has been killed! \n")
        elif signum == signal.SIGTERM:
            self.end_connexion()
            print("SIGTERM signal raised!")
            print(" Servomotor Server Process has been terminated! \n")
            syslog.syslog(syslog.LOG_ERR, " Servomotor Server Process has been terminated! \n")
        elif signum == signal.SIGTSTP:
            self.end_connexion()
            print("SIGTSTP signal raised!")
            print(" Servomotor Server Process has been stopped! \n")
            syslog.syslog(syslog.LOG_ERR, " Servomotor Server Process has been stopped! \n")

if __name__ == "__main__":
    print("Launching " + sys.argv[0])
    syslog.syslog(syslog.LOG_INFO, "Launching " + sys.argv[0] + "\n")
    #Default argument value (for initialization)
    gpio_pin = None
    host = "localhost"
    port = 9000
    buffer_size = 1024
    timeout = 300
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hgipbt", ["help", "gpio_pin", "ip", "port", "buffer_size", "timeout"])
    except getopt.GetoptError as err:
        print(err)
        print("\n")
        print("Wrong arguments or Not enough arguments")
        print("Usage :")
        print("Servomotor_servo -g gpio_pin -i hostname -p port -b buffer_size -t timeout")
        print(" or")
        print("Servomotor_servo -gpio_pin gpio_pin --ip hostname --port port --buffer_size buffer_size --timeout timeout")
        print("Quitting the program!")
        syslog.syslog(syslog.LOG_ERR, "Quitting the program!\n")
        sys.exit(2)
    for o, a in opts:
        if o in ("-h", "--help"):
            print("Options and arguments : ")
            print("-h or --help : Display this help message")
            print("-g or --gpio_pin : Required. Board pin of the RPi to which the servomotor pin control will be attached")
            print("-i or --ip : Default is localhost. Ip Address of the RPi on which the server is running. ")
            print("-p or --port : Default is 9000. Port of the RPi on which the server is running")
            print("-b or --buffer_size : Default is 1024. Buffer size in bytes for receiving the command data for the client")
            print("-t or --timeout : Default is 300. Time in seconds before the server will end.")
            print("\n")
            print("Usage :")
            print("Servomotor_servo -g gpio_pin -i hostname -p port -b buffer_size -t timeout")
            print(" or")
            print("Servomotor_servo -gpio_pin gpio_pin --ip hostname --port port --buffer_size buffer_size --timeout timeout")
            print("Quitting the program!")
            syslog.syslog(syslog.LOG_ERR, "Quitting the program!\n")
            sys.exit()
        elif o in ("-g", "--gpio_pin"):
            gpio_pin = a
        elif o in ("-i", "--ip"):
            host = a
        elif o in ("-p", "--port"):
            port = a
        elif o in ("-b", "--buffer_size"):
            buffer_size = a
        elif o in ("-t", "--timeout"):
            timeout = a
        else:
            assert False, "unhandled option"
            print("Quitting the program!")
            syslog.syslog(syslog.LOG_ERR, "Quitting the program!\n")
            sys.exit(1)
    
    if not (gpio_pin is None):
        Server = Servomotor_server(host, port, buffer_size, timeout)
    else:
        print("Missing gpio_pin")
        print("Usage :")
        print("Servomotor_servo -g gpio_pin -i hostname -p port -b buffer_size -t timeout")
        print(" or ")
        print("Servomotor_servo -gpio_pin gpio_pin --ip hostname --port port --buffer_size buffer_size --timeout timeout")
        print("Quitting the program!")
        syslog.syslog(syslog.LOG_ERR, "Quitting the program!\n")
        sys.exit(2)



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
        try:
            # Receive command
            data = Server.conn.recv(Server.buffer_size)
            angle = bytes_to_int(data)
            if angle == 0 :
                print("[ {} ] Value 0 has been received. Stopping the communication.\n".format( Server.addr))
                syslog.syslog(syslog.LOG_INFO,"[ {} ] Value 0 has been received. Stopping the communication.\n".format( Server.addr))
                print("[ {} ] Client disconnected from server \n".format(Server.addr))
                syslog.syslog(syslog.LOG_INFO, "[ {} ] Client disconnected from server \n".format(Server.addr))
                print("[ {} ] Closing the server\n".format(Server.addr))
                syslog.syslog(syslog.LOG_INFO, "[ {} ] Closing the server\n".format(Server.addr))
                Server.end_connexion()
                break
            if angle <0 or angle > 180:
                print("[ {} ] Wrong value for angle : {} \n".format(Server.addr, angle))
                syslog.syslog(syslog.LOG_ERR, "[ {} ] Wrong value for angle : {} \n".format(Server.addr, angle))
            else:
                # Move the servomotor
                #Server.control_servomotor()
                print("[ {} ] Value send is {} \n".format(Server.addr, angle))
                syslog.syslog(syslog.LOG_INFO, "[ {} ] Value send is {} \n".format(Server.addr, angle))
        except socket.timeout:
            print("[ {} ] Client disconnected from server \n".format(Server.addr))
            syslog.syslog(syslog.LOG_ERR, "[ {} ] Client disconnected from server \n".format(Server.addr))
            print("[ {} ] Closing the server\n".format(Server.addr))
            syslog.syslog(syslog.LOG_ERR, "[ {} ] Closing the server\n".format(Server.addr))
            Server.timeout()
            syslog.syslog(syslog.LOG_ERR, "Server timeout, exiting the program...")
            break
    
    sys.exit(0)
