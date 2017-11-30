from flask import Flask, request
import RPi.GPIO as GPIO
import time
import zeroconf
import socket

app = Flask(__name__)

# Module level constants
#Globals
RED = 5
GREEN = 19
BLUE = 26
r = None
g = None
b = None

# Sets up pins as outputs
def setup(*leds):
    global r
    global g
    global b
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for led in leds:
        GPIO.setup(led, GPIO.OUT)
        GPIO.output(led, GPIO.LOW)
    f = 100
    r = GPIO.PWM(RED, f)
    g = GPIO.PWM(GREEN, f)
    b = GPIO.PWM(BLUE, f)
    return None

# Setup leds
setup(RED, GREEN, BLUE)


@app.route('/LED')
def LED(status, color, intensity):
    if(status == 'on'):
        if(color == 'red'):
            red_on(int(intensity))
        elif(color == 'green'):
            green_on(int(intensity))
        elif(color == 'blue'):
            blue_on(int(intensity))
        elif(color == 'magenta'):
            magenta_on(int(intensity))
        elif(color == 'cyan'):
            cyan_on(int(intensity))
        elif(color == 'yellow'):
            yellow_on(int(intensity))
        elif(color == 'white'):
            white_on(int(intensity))
        else:
            print("Error: unknown color, color = ", color)
    elif(status == 'off'):
        turn_off()#turn off LED
    else:
        print("Error: unknown status, status = ", status)
    return None

def turn_off():
    r.start(0)
    b.start(0)
    g.start(0)
    return None

def red_on(intensity):
    turn_off()
    #turn on red
    r.start(int(intensity))
    return None

def blue_on(intensity):
    #turn off green and red
    turn_off()
    #turn on blue
    b.start(int(intensity))
    return None

def green_on(intensity):
    #turn off blue and red
    turn_off()
    #turn on green
    g.start(int(intensity))
    return None

def magenta_on(intensity):
    #turn off green
    turn_off()
    #turn on blue and red
    r.start(int(intensity))
    b.start(int(intensity))
    return None

def cyan_on(intensity):
    #turn off red
    turn_off()
    #turn on blue and green
    b.start(int(intensity))
    g.start(int(intensity))
    return None

def yellow_on(intensity):
    #turn off blue
    turn_off()
    #turn on red and green
    r.start(int(intensity))
    g.start(int(intensity))
    return None

def white_on(intensity):
    #turn on all
    r.start(int(intensity))
    b.start(int(intensity))
    g.start(int(intensity))
    return None
    

if __name__ == '__main__':
    host = '172.29.81.174'
    info = zeroconf.ServiceInfo("_http._tcp.local.",
                       "LED PI._http._tcp.local.",
                       socket.inet_aton("172.29.81.174"), 800, 0, 0,
                       {'Available Colors': "'red', 'blue', 'green', 'yellow', 'cyan', 'magenta', 'white'"}, "ash-2.local.")
    zconf = zeroconf.Zeroconf()
    zconf.register_service(info)
    app.run(host, port=800, debug=False)
    try:
        while True:
            sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        zconf.unregister_service(info)
        zconf.close()