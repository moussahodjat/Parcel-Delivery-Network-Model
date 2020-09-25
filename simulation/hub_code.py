#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 16:43:24 2020

@author: Moussa
"""
'''
class Hub:
    def __init__(self, main_object):
        self.site_code = None
        self.latitude = None
        self.longitude = None
        self.main_object = main_object
    
    
    def parcel_arriving(self, p):
        # print('parcel arriving at date ' + str(self.main_object.convert_to_date(self.main_object.env.now)))
        self.main_object.router.notify_parcel_ready_to_dispatch(self.site_code, p)
        
        
        
    def vehicle_arriving_for_loading(self, v):
        #print('vehicle arriving at date ' + str(self.main_object.convert_to_date(self.main_object.env.now)))
        loading_list = self.main_object.router.request_loading(self.site_code, v)
        load = 0
        for p in loading_list:
            v.load_parcel(p)
            load += p.weight
        if load > v.capacity:
            print('vehicle capacity error')
            raise
        v.move_to_next_destination()
    
    
    def vehicle_arriving_for_unloading(self, v):
        self.main_object.router.notify_vehicle_reached_final_destination(self.site_code, v)
        for p in v.loaded_parcels:
            if p.dest_gh == self.site_code:
                self.main_object.router.notify_parcel_reached_final_destination(self.site_code, p)
            else:
                self.main_object.router.notify_parcel_ready_to_dispatch(self.site_code, p)
            

if __name__ == "__main__":
    import main
    print('main imported in hub code')
        
'''