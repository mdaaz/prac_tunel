"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "north"
NORTH = "south"

NCARS = 10

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.cars_north = Value('i',0)
        self.cars_south = Value('i',0)
        self.inside_north = Value('i',0)
        self.inside_south = Value('i',0)
        self.semaphore = Value('i',0)
        self.open_south = Condition(self.mutex)
        self.open_north = Condition(self.mutex)
        
    def no_cars_north(self):
        return self.inside_north.value == 0 \
               and (self.cars_north.value == 0 or self.semaphore.value == 1)
    
    def no_cars_south(self):
        return self.inside_south.value == 0 \
               and (self.cars_south.value == 0 or self.semaphore.value == 0)
        
    def wants_enter(self, direction):
        self.mutex.acquire()
        if direction == "north":
            self.cars_north.value += 1
            self.open_north.wait_for(self.no_cars_south)
            self.inside_north.value += 1
            self.cars_north.value -= 1
        elif direction == "south":
            self.cars_south.value += 1
            self.open_south.wait_for(self.no_cars_north)
            self.inside_south.value += 1
            self.cars_south.value -= 1
        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()
        if direction == "north":
            self.inside_north.value -= 1
            if self.inside_north.value == 0:
                self.semaphore.value = 1
                self.open_south.notify_all()
        elif direction == "south":
            self.inside_south.value -= 1
            if self.inside_south.value == 0:
                self.semaphore.value = 0
                self.open_north.notify_all()
        self.mutex.release()

def delay(n=3):
    time.sleep(random.random()*n)

def car(cid, direction, monitor):
    print(f"car {cid} direction {direction} created")
    delay(6)
    print(f"car {cid} heading {direction} wants to enter")
    monitor.wants_enter(direction)
    print(f"car {cid} heading {direction} enters the tunnel")
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")
    



def main():
    monitor = Monitor()
    cid = 0
    for i in range(NCARS):
        direction = NORTH if i%2==1  else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1/0.5)) # a new car enters each 0.5s
        
main()