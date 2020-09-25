#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 16:57:12 2020

@author: Moussa
"""

class Vehicle:
    def __init__(self, main_object):
        self.main_object = main_object
        self.id = None
        #self.input_id = None
        self.orig_gh = None
        self.orig_time = None
        self.dest_gh = None
        self.dest_time = None
        self.capacity = None
        self.orig_date = None
        self.dest_date = None
        self.loaded_parcels = [] 
        self.load = 0
        self.dispatch_vehicles= {} # {input_id: [cap] }
    
    def load_parcel(self, p):
        self.loaded_parcels.append(p)
        self.load += p.weight
        
        
    def move_to_next_destination(self):
        self.main_object.env.process(self.schedule_moving())
    
    def schedule_moving(self):
        #1.	moving delay with priority 2
        delay = self.dest_time - self.main_object.env.now
        self.main_object.simpy.events.NORMAL = 2
        event = self.main_object.simpy.events.Timeout(self.main_object.env, delay)
        self.main_object.simpy.events.NORMAL = 1
        yield event
        
        #2. calls vehicle_arriving_for_unloading at dest
        self.main_object.router.unloading_request(self)
        
    
    
    
    
if __name__ == '__main__':
    import main
    print('main imported in vehicle code')
    
    
