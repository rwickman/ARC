import time
from threading import Thread
from .memory import Memory
from .log import get_logger
import RPi.GPIO as GPIO
import time
from .classifier import Classifier #Classifer.py will need to be included in the same directory as vehicle.py 

GPIO_TRIGGER = 23
GPIO_ECHO = 24
GPIO.setmode(GPIO.BCM)

GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

logger = get_logger(__name__)
# TODO
## Should add the ultrasonic sensor as a part
## The ultrasonic sensor code should be in its won class
## maybe have the thread return a value rather than have it set the shouldStop variable
## make n_times an argument to Vehicle() and a CLI argument to manage.py
## Look into how GPIO actually works

class Vehicle:
    def __init__(self, mem=None):
        if not mem:
            mem = Memory()
        self.mem = mem
        self.parts = [] # Turn this into an array where the name is the key
        self.on = True
        self.threads = []
        self.shouldStop = False
        self.MIN_DISTANCE_TO_OBJECT = 50
        self.ultrasonic_sensor_wait = 0.25
        self.n = 13
        self.n_times_wait_reduction = 0.15
        self.classifier = Classifier()
        self.acc = None

    def add(self, part, inputs=[], outputs=[],
            threaded=False, run_condition=None, name=None):
        """
        Method to add a part to the vehicle drive loop.

        Parameters
        i----------
            inputs : list
                Channel names to get from memory.
            outputs : list
                Channel names to save to memory.
            threaded : boolean
                If a part should be run in a separate thread.
            run_condition: boolean
                If a part should be run at all.
        """

        p = part
        logger.info('Adding part {}.'.format(p.__class__.__name__))
        entry = dict()
        entry['part'] = p
        entry['inputs'] = inputs
        entry['outputs'] = outputs
        entry['run_condition'] = run_condition
        entry['name'] = name
        if name == "PWMThrottle":
            self.acc = p
        if threaded:
            t = Thread(target=part.update, args=())
            t.daemon = True
            entry['thread'] = t
        self.parts.append(entry)

    def start(self, rate_hz=10, max_loop_count=None):
        """
        Start vehicle's main drive loop.

        This is the main thread of the vehicle. It starts all the new
        threads for the threaded parts then starts an infinit loop
        that runs each part and updates the memory.

        Parameter1s
        ----------

        rate_hz : int
            The max frequency that the drive loop should run. The actual
            frequency may be less than this if there are many blocking parts.
        max_loop_count : int
            Maxiumum number of loops the drive loop should execute. This is
            used for testing the all the parts of the vehicle work.
        """

        try:
            self.on = True

            for entry in self.parts:
                if entry.get('thread'):
                    # start the update thread
                    entry.get('thread').start()

            # wait until the parts warm up.
            logger.info('Starting vehicle...')
            time.sleep(1)
            get_distance_thread = Thread(target=self.get_distance)
            get_distance_thread.start()
            classifier_thread = Thread(target=self.classifier.predict)
            loop_count = 0
            #distance = 0
            while self.on:
                start_time = time.time()
                loop_count += 1
                if not self.shouldStop:
                    self.update_parts()
                else:
                    self.acc.run(0)
                    print("OBJECT IN THE WAY")
                    self.check_distance_n_times(self.n)

                # stop drive loop if loop_count exceeds max_loopcount
                if max_loop_count and loop_count > max_loop_count:
                    self.on = False

                sleep_time = 1.0 / rate_hz - (time.time() - start_time)
                if sleep_time > 0.0:
                    time.sleep(sleep_time)

        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def update_parts(self):
        """
        loop over all parts
        """
        print("updating parts")
        for entry in self.parts:
            # don't run if there is a run condition that is False
            run = True
            if entry.get('run_condition'):
                run_condition = entry.get('run_condition')
                run = self.mem.get([run_condition])[0]
                # print('run_condition', entry['part'], entry.get('run_condition'), run)

            if run:
                p = entry['part']
                # get inputs from memory
                inputs = self.mem.get(entry['inputs'])

                # run the part
                if entry.get('thread'):
                    outputs = p.run_threaded(*inputs)
                    if entry['name'] == "cam":
                        predicted = self.classifier.predict(outputs)
                        print("PREDICTED: ", predicted)
                        if predicted:
                            self.shouldStop = True
                else:
                    outputs = p.run(*inputs)
                # save the output to memory
                if outputs is not None:
                    self.mem.put(entry['outputs'], outputs)

    def stop(self):
        logger.info('Shutting down vehicle and its parts...')
        for entry in self.parts:
            try:
                entry['part'].shutdown()
            except Exception as e:
                logger.debug(e)

    def get_distance(self):
        while self.on:
            # set Trigger to HIGH
            
            # set Trigger after 0.01ms to LOW
            time.sleep(self.ultrasonic_sensor_wait)
            
            if not self.shouldStop:
                GPIO.output(GPIO_TRIGGER, True)
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
                distance = (TimeElapsed * 34300) / 2
                print("DISTANCE: ", distance)
                if distance < self.MIN_DISTANCE_TO_OBJECT:
                    self.shouldStop = True
                    #time.sleep(self.stop_wait_time_end)
        
#return distance
    # check if the blocking object is not there
    ## it has to verify that the object is not there for num_checks sequentially
    
    ## This will also have the effect of wating a minumum of num_checks * (self.ultrasonic_sensor_wait - self.n_time_reductio)n
    ## This method and self.get_distance should either combine into one or have a third method that handles there similaritys
    def check_distance_n_times(self, num_checks):
        verify = 0
        while verify < num_checks:
            print("VERIFY: ", verify) 
            # set Trigger to HIGH
            GPIO.output(GPIO_TRIGGER, True)

            # set Trigger after 0.01ms to LOW
            time.sleep(max(self.ultrasonic_sensor_wait - self.n_times_wait_reduction,  0.0))
            GPIO.output(GPIO_TRIGGER, False)

            StartTime = time.time()
            StopTime = time.time()

            # save StartTime
            while GPIO.input(GPIO_ECHO) == 0:
                StartTime = time.time()

            # save time of arrival
            while GPIO.input(GPIO_ECHO) == 1:
                StopTime = time.time()

            # time difference between start and arrival
            TimeElapsed = StopTime - StartTime
            # multiply with the sonic speed (34300 cm/s)
            # and divide by 2, because there and back
            distance = (TimeElapsed * 34300) / 2
            print("DISTANCE(n_times): ", distance)
            if distance < self.MIN_DISTANCE_TO_OBJECT:
                verify = 0
            else:
                verify += 1
        self.shouldStop = False 
