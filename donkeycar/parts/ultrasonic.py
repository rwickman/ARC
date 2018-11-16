import RPi.GPIO as GPIO
import time

GPIO_TRIGGER = 23
GPIO_ECHO = 24
GPIO.setmode(GPIO.BCM)

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

class Ultrasonic:

    def __init__(self, n = 10):
        self.ultrasonic_sensor_wait = 0.025
        self.n = n
        self.distance = 0
        self.on = True

    def run_threaded(self):
        return self.distance

    # Set distance
    def update(self):
        while self.on:
            time.sleep(self.ultrasonic_sensor_wait)
                 # set Trigger to HIGH
            GPIO.output(GPIO_TRIGGER, True)
            # set Trigger after 0.01ms to LOW
            time.sleep(0.001)
            GPIO.output(GPIO_TRIGGER, False)

            StartTime = time.time()
            StopTime = time.time()

            # save StartTime
            while GPIO.input(GPIO_ECHO) == 0:
                pass
            
            StartTime = time.time()

            # save time of arrival
            while GPIO.input(GPIO_ECHO) == 1:
                pass
                
            StopTime = time.time()

            # time difference between start and arrival
            TimeElapsed = StopTime - StartTime
                # multiply with the sonic speed (34300 cm/s)
            # and divide by 2, because there and back
            self.distance = (TimeElapsed * 34300) / 2
            print("DISTANCE: ", self.distance)

    # check if the blocking object is not there
    ## it has to verify that the object is not there for num_checks sequentially
    
    ## This will also have the effect of waiting a minumum of num_checks * (self.ultrasonic_sensor_wait - self.n_time_reductio)n
    ## This method and self.get_distance should either combine into one or have a third method that handles there similaritys
