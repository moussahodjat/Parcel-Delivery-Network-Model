#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May 14 20:01:23 2020

@author: Moussa
"""


if __name__ == "__main__":
    print("main imported to demand genearator code")
    import main
    


class DemandGenerator():
    
    def __init__(self, main_object):
        self.main = main_object
        self.schedule_all_demand()
        
        
       
        
    def schedule_all_demand(self):
        # t0 = self.main.time.time()
        # print(self.main.inputs.demand_file_name)
        df = self.main.pd.read_csv(self.main.inputs.demand_file_name)
        # print('reading demand ', self.main.inputs.demand_file_name)
        for index, row in df.iterrows():
            #print(row)
            input_id = row['input_id']
            orig_date = self.main.pd.to_datetime(row['orig_date'])
            orig_time = self.main.convert_to_simulation_time(orig_date)
            orig_gh = row['orig_gh']
            dest_date = self.main.pd.to_datetime(row['dest_date'])
            dest_time = self.main.convert_to_simulation_time(dest_date)
            dest_gh = row['dest_gh']
            weight = float(row['weight'])
            self.main.router.demand_expected(orig_gh, dest_gh, orig_date, dest_date, weight)
            self.main.env.process(self.schedule_demand(input_id, orig_time, orig_gh, dest_time, dest_gh, weight))
        # print('scheduling demands took %s ' % (self.main.time.time() - t0))
        # print("_____________________")
        
    
    
    def schedule_demand(self,input_id, orig_time, orig_gh, dest_time, dest_gh, weight):
        #1.	router.parcel_expected is called
        #this is done in the schedule_all_demand function
        #2. delay
        yield self.main.env.timeout(orig_time)
        #3. router.demand_realized
        p = self.main.parcel_code.Parcel(self.main)
        p.orig_time = orig_time
        p.orig_gh = orig_gh
        p.dest_time = dest_time
        p.dest_gh = dest_gh
        p.weight = weight
        p.input_id = input_id
        p.orig_date = self.main.convert_to_date(orig_time)
        p.dest_date = self.main.convert_to_date(dest_time)
        self.main.router.demand_realized(orig_gh, dest_gh, p.orig_date, p.dest_date, weight,[p])

        
    
    
    
    
    
    
    
    
    
    
    
    
    