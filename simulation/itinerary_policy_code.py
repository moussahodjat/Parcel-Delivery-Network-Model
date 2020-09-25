#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 20 01:38:59 2020

@author: Moussa
"""

class ItineraryPolicy:
    def __init__(self, main_object):
        self.main_object = main_object
        self.itineraries = {} #parcel input id -> [(orig_gh, orig_date, dest_gh), (orig_gh, orig_date, dest_gh)...]
        self.initialize_itineraries()
        #self.schedule_vehicles()
        
        
        
    def initialize_itineraries(self):
        # t0 = self.main_object.time.time()
        df = self.main_object.pd.read_csv(self.main_object.inputs.itineraries_file_name)
        for index, row in df.iterrows():
            input_id = row['input_id']
            itinerary = row['itinerary'].split("&")
            a_list = [] 
            for item in itinerary:
                orig_gh, orig_date, dest_gh = item.split("_")
                a_list.append((orig_gh, self.main_object.pd.to_datetime(orig_date), dest_gh))
            self.itineraries[input_id] = a_list  
        # print('initializing itineraries took %s' %(self.main_object.time.time() - t0))
        # print("_________________")
    

    # def schedule_vehicles(self):
    #     t0 = self.main_object.time.time()
    #     df_vehicles = self.main_object.pd.read_csv(self.main_object.inputs.vehicles_file_name)
    #     for index, row in df_vehicles.iterrows():
    #         orig_date = self.main_object.pd.to_datetime(row['orig_date'])
    #         orig_gh = row['orig_gh']
    #         dest_gh = row['dest_gh']
    #         capacity = float(row['capacity'])
    #         input_id = row['input_id']
    #         self.main_object.env.process(self.main_object.router.schedule_vehicle(input_id, orig_gh, dest_gh,orig_date, capacity))
    #     print('scheduling vehicles took %s ' % (self.main_object.time.time() - t0))
    #     print("____________")


    def parcel_created(self, p):
        for dispatch in self.itineraries[p.input_id]:
            veh_orig, veh_orig_date, veh_dest = dispatch
            self.main_object.router.assign_parcels_to_vehicle([p], veh_orig, veh_dest, veh_orig_date)





if __name__ == "__main__":
    import main
    print('main imported in itinerary policy code')
    
    
    
    
    
    
    
    
    
    
    
    
    
    