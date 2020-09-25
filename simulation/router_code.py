#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 18 16:32:05 2020

@author: Moussa
"""

class Router:
    def __init__(self, main_object):
        self.main = main_object
        self.parcel_id = 1
        self.vehicle_id = 1
        self.veh_cap = {}    #{ogh: {dgh: {od: {dd: capacity}}}
        self.veh_parcel_assignment = {}  #{(ogh, dgh, od): [parcels]}
        self.rtd_demand = {}#{ogh: {dgh: {dd: [parcels]}}}
        self.en_route_demand = {} #{ogh: {dgh: {od: {dd: [parcels]}}}
        self.future_demand = {} #{ogh: {dgh: {od: {dd: mean}}}
        self.dispatch_vehicles = {} #{ogh : {dgh: {od: input_id: [veh_cap]}}}
        self.schedule_planned_vehicles()
        
    
    def add_to_dispatch_vehicles(self, orig_gh, dest_gh, orig_date, input_id, veh_cap):
        if orig_gh not in self.dispatch_vehicles:
            self.dispatch_vehicles[orig_gh] = {}
        if dest_gh not in self.dispatch_vehicles[orig_gh]:
            self.dispatch_vehicles[orig_gh][dest_gh] = {}
        if orig_date not in self.dispatch_vehicles[orig_gh][dest_gh]:
            self.dispatch_vehicles[orig_gh][dest_gh][orig_date] = {}
        if input_id not in self.dispatch_vehicles[orig_gh][dest_gh][orig_date]:
            self.dispatch_vehicles[orig_gh][dest_gh][orig_date][input_id] = []
        self.dispatch_vehicles[orig_gh][dest_gh][orig_date][input_id].append(veh_cap)
    def remove_from_dispatch_vehicles(self, orig_gh, dest_gh, orig_date, input_id, veh_cap):
        self.dispatch_vehicles[orig_gh][dest_gh][orig_date][input_id].remove(veh_cap)
        if len(self.dispatch_vehicles[orig_gh][dest_gh][orig_date][input_id]) == 0:
            del self.dispatch_vehicles[orig_gh][dest_gh][orig_date][input_id]
            if not self.dispatch_vehicles[orig_gh][dest_gh][orig_date]:
                del self.dispatch_vehicles[orig_gh][dest_gh][orig_date]
                if not self.dispatch_vehicles[orig_gh][dest_gh]:
                    del self.dispatch_vehicles[orig_gh][dest_gh]
                    if not self.dispatch_vehicles[orig_gh]:
                        del self.dispatch_vehicles[orig_gh]
    def add_to_veh_cap_dic(self, orig_gh, dest_gh, orig_date, dest_date, capacity):
        if orig_gh not in self.veh_cap:
            self.veh_cap[orig_gh] = {}
        if dest_gh not in self.veh_cap[orig_gh]:
            self.veh_cap[orig_gh][dest_gh] = {}
        if orig_date not in self.veh_cap[orig_gh][dest_gh]:
            self.veh_cap[orig_gh][dest_gh][orig_date] = {}
        if dest_date not in self.veh_cap[orig_gh][dest_gh][orig_date]:
            self.veh_cap[orig_gh][dest_gh][orig_date][dest_date] = 0.0
        self.veh_cap[orig_gh][dest_gh][orig_date][dest_date] = round(capacity + self.veh_cap[orig_gh][dest_gh][orig_date][dest_date] ,3)       
    def remove_from_veh_cap_dic(self, orig_gh, dest_gh, orig_date, dest_date, capacity):
        if round(capacity,3) == 0:
            return
        # print(orig_gh, dest_gh, orig_date, dest_date, capacity)
        self.veh_cap[orig_gh][dest_gh][orig_date][dest_date] = round(- capacity + self.veh_cap[orig_gh][dest_gh][orig_date][dest_date],3)
        if self.veh_cap[orig_gh][dest_gh][orig_date][dest_date] < 0:
            print(orig_gh, dest_gh, orig_date, dest_date, self.veh_cap[orig_gh][dest_gh][orig_date][dest_date])
            raise
        if self.veh_cap[orig_gh][dest_gh][orig_date][dest_date] == 0:
            del self.veh_cap[orig_gh][dest_gh][orig_date][dest_date]
            if not self.veh_cap[orig_gh][dest_gh][orig_date]:
                del self.veh_cap[orig_gh][dest_gh][orig_date]
                if not self.veh_cap[orig_gh][dest_gh]:
                    del self.veh_cap[orig_gh][dest_gh]
                    if not self.veh_cap[orig_gh]:
                        del self.veh_cap[orig_gh]
    def add_to_veh_parcel_assignment(self, orig_gh, dest_gh, orig_date, parcels):
        if orig_gh not in self.veh_parcel_assignment:
            self.veh_parcel_assignment[orig_gh] = {}
        if dest_gh not in self.veh_parcel_assignment[orig_gh]:
            self.veh_parcel_assignment[orig_gh][dest_gh] = {}
        if orig_date not in self.veh_parcel_assignment[orig_gh][dest_gh]:
            self.veh_parcel_assignment[orig_gh][dest_gh][orig_date] = []
        for p in parcels:
            self.veh_parcel_assignment[orig_gh][dest_gh][orig_date].append(p)        
    def remove_from_veh_parcel_assignment(self, orig_gh, dest_gh, orig_date, parcels):
        for p in parcels:
            self.veh_parcel_assignment[orig_gh][dest_gh][orig_date].remove(p)
        if len(self.veh_parcel_assignment[orig_gh][dest_gh][orig_date]) == 0:
            del self.veh_parcel_assignment[orig_gh][dest_gh][orig_date]
            if not self.veh_parcel_assignment[orig_gh][dest_gh]:
                del self.veh_parcel_assignment[orig_gh][dest_gh]
                if not self.veh_parcel_assignment[orig_gh]:
                    del self.veh_parcel_assignment[orig_gh]                   
    def add_to_rtd_demand(self, orig_gh, dest_gh, due_date, parcels):
        if orig_gh not in self.rtd_demand:
            self.rtd_demand[orig_gh] = {}
        if dest_gh not in self.rtd_demand[orig_gh]:
            self.rtd_demand[orig_gh][dest_gh] = {}
        if due_date not in self.rtd_demand[orig_gh][dest_gh]:
            self.rtd_demand[orig_gh][dest_gh][due_date] = [] 
        for p in parcels:
            self.rtd_demand[orig_gh][dest_gh][due_date].append(p)      
    def remove_from_rtd_demand(self, orig_gh, dest_gh, due_date, parcels):
        for p in parcels:
            self.rtd_demand[orig_gh][dest_gh][due_date].remove(p)
        if len(self.rtd_demand[orig_gh][dest_gh][due_date]) == 0:
            del self.rtd_demand[orig_gh][dest_gh][due_date]
            if not self.rtd_demand[orig_gh][dest_gh]:
                del self.rtd_demand[orig_gh][dest_gh]
                if not self.rtd_demand[orig_gh]:
                    del self.rtd_demand[orig_gh]                
    def add_to_en_route_demand(self, orig_gh, dest_gh, orig_date, dest_date, parcels):
        if orig_gh not in self.en_route_demand:
            self.en_route_demand[orig_gh] = {} 
        if dest_gh not in self.en_route_demand[orig_gh]:
            self.en_route_demand[orig_gh][dest_gh] = {} 
        if orig_date not in self.en_route_demand[orig_gh][dest_gh]:
            self.en_route_demand[orig_gh][dest_gh][orig_date] = {}
        if dest_date not in self.en_route_demand[orig_gh][dest_gh][orig_date]:
            self.en_route_demand[orig_gh][dest_gh][orig_date][dest_date] = [] 
        for p in parcels:
            self.en_route_demand[orig_gh][dest_gh][orig_date][dest_date].append(p)        
    def remove_from_en_route_demand(self, orig_gh, dest_gh, orig_date, dest_date, parcels):
        for p in parcels:
            self.en_route_demand[orig_gh][dest_gh][orig_date][dest_date].remove(p)
        if len(self.en_route_demand[orig_gh][dest_gh][orig_date][dest_date]) == 0:
            del self.en_route_demand[orig_gh][dest_gh][orig_date][dest_date]
            if not self.en_route_demand[orig_gh][dest_gh][orig_date]:
                del self.en_route_demand[orig_gh][dest_gh][orig_date]
                if not self.en_route_demand[orig_gh][dest_gh]:
                    del self.en_route_demand[orig_gh][dest_gh]
                    if not self.en_route_demand[orig_gh]:
                        del self.en_route_demand[orig_gh]           
    def add_to_future_demand(self, orig_gh, dest_gh, orig_date, dest_date, amount):
        if orig_gh not in self.future_demand:
            self.future_demand[orig_gh] = {} 
        if dest_gh not in self.future_demand[orig_gh]:
            self.future_demand[orig_gh][dest_gh] = {} 
        if orig_date not in self.future_demand[orig_gh][dest_gh]:
            self.future_demand[orig_gh][dest_gh][orig_date] = {}
        if dest_date not in self.future_demand[orig_gh][dest_gh][orig_date]:
            self.future_demand[orig_gh][dest_gh][orig_date][dest_date] = 0 
        self.future_demand[orig_gh][dest_gh][orig_date][dest_date] = round(amount + self.future_demand[orig_gh][dest_gh][orig_date][dest_date],3)           
    def remove_from_future_demand(self, orig_gh, dest_gh, orig_date, dest_date, amount):
        self.future_demand[orig_gh][dest_gh][orig_date][dest_date] = round(- amount + self.future_demand[orig_gh][dest_gh][orig_date][dest_date],3)
        if self.future_demand[orig_gh][dest_gh][orig_date][dest_date] < 0:
            print(orig_gh,dest_gh,orig_date,dest_date)
            print(self.future_demand[orig_gh][dest_gh][orig_date][dest_date])
            raise
        if self.future_demand[orig_gh][dest_gh][orig_date][dest_date] == 0:
            del self.future_demand[orig_gh][dest_gh][orig_date][dest_date]
            if not self.future_demand[orig_gh][dest_gh][orig_date]:
                del self.future_demand[orig_gh][dest_gh][orig_date]
                if not self.future_demand[orig_gh][dest_gh]:
                    del self.future_demand[orig_gh][dest_gh]
                    if not self.future_demand[orig_gh]:
                        del self.future_demand[orig_gh]
       
        
       
        
    def demand_expected(self, orig_gh, dest_gh, orig_date, dest_date, amount):
        #1.	add to future_demand
        self.add_to_future_demand(orig_gh, dest_gh, orig_date, dest_date, amount)

        
    def demand_realized(self, orig_gh, dest_gh, orig_date, dest_date, expected_amount, parcels):
        #0. call parcel_created in record statistics
        #1.	set id
        for p in parcels:
            self.main.record_statistics.notify_parcel_created(p)
            p.id = self.parcel_id
            self.parcel_id += 1
        #2.	remove expected amount from future_demand
        self.remove_from_future_demand(orig_gh, dest_gh, orig_date, dest_date, expected_amount)
        #3.add the parcel to rtd_demand
        self.add_to_rtd_demand(orig_gh, dest_gh, dest_date, parcels)
        #4.if itinerary policy, call itinerary policy
        if self.main.inputs.policy_name == "itinerary":
            for p in parcels:
                self.main.itinerary_policy.parcel_created(p)
            



    def schedule_vehicle(self,input_id, orig_gh, dest_gh, orig_date, capacity):
        #   1.	call notify_vehicle_scheduled in record_statistics
        self.main.record_statistics.notify_vehicle_scheduled(orig_gh, dest_gh, capacity)
        # 	2.	add to veh_cap
        orig_time = self.main.convert_to_simulation_time(orig_date)
        dest_time = orig_time + self.main.inputs.travel_times[orig_gh][dest_gh]
        dest_date = self.main.convert_to_date(dest_time)
        self.add_to_veh_cap_dic(orig_gh, dest_gh, orig_date, dest_date, capacity)
        # 	3.	if the key already exists in the dispatch_vehicles dic, dispatch_already_scheduled = True
        dispatch_already_scheduled = False
        if orig_gh in self.dispatch_vehicles:
            if dest_gh in self.dispatch_vehicles[orig_gh]:
                if orig_date in self.dispatch_vehicles[orig_gh][dest_gh]:
                    dispatch_already_scheduled = True      
                    # print('dispatch_already_scheduled')
        # 	4.	add to dispatch_vehicles 
        self.add_to_dispatch_vehicles(orig_gh, dest_gh, orig_date, input_id, capacity)
        # 	5.	if dispatch_already_scheduled: return
        if not dispatch_already_scheduled:
            #the second function
            self.main.env.process(self.schedule_vehicle2(orig_gh, dest_gh, orig_date, orig_time, dest_date, dest_time))



    def schedule_vehicle2(self, orig_gh, dest_gh, orig_date, orig_time, dest_date, dest_time):
        # 	6.	delay with priority 4
        delay = orig_time - self.main.env.now
        self.main.simpy.events.NORMAL = 4
        event = self.main.simpy.events.Timeout(self.main.env, delay)
        self.main.simpy.events.NORMAL = 1
        yield event
        # 	7.	create vehicle, set id, v.capacity, v.dispatch_vehicles
        v = self.main.vehicle_code.Vehicle(self.main)
        v.id = self.vehicle_id
        self.vehicle_id += 1
        v.orig_time = orig_time
        v.orig_gh = orig_gh
        v.dest_time = dest_time
        v.dest_gh = dest_gh
        v.orig_date = orig_date
        v.dest_date = dest_date
        v.capacity = 0
        for input_id in self.dispatch_vehicles[orig_gh][dest_gh][orig_date]:
            v.dispatch_vehicles[input_id] = [] 
            for cap in self.dispatch_vehicles[orig_gh][dest_gh][orig_date][input_id]:
                v.capacity += cap
                v.dispatch_vehicles[input_id].append(cap)
        # 	8.	call notify_vehicle_created in record statistics
        self.main.record_statistics.notify_vehicle_created(v)
        # 	9.	call load request
        self.loading_request(v)
        
        
    def assign_parcels_to_vehicle(self, parcels, veh_orig, veh_dest, veh_orig_date):
        orig_time = self.main.convert_to_simulation_time(veh_orig_date)
        veh_dest_date = self.main.convert_to_date(orig_time + self.main.inputs.travel_times[veh_orig][veh_dest])
        total_weight = sum(p.weight for p in parcels)
        #0. if vehicle not in veh_cap or cap not enough for parcels, raise error
        try:
            remaining_cap = self.veh_cap[veh_orig][veh_dest][veh_orig_date][veh_dest_date] 
        except:
            raise
        if total_weight > remaining_cap:
            print("error in router.assign_parcels_to_vehicle")
            raise
        #1.	add parcels to veh_parcel_assignment
        self.add_to_veh_parcel_assignment(veh_orig, veh_dest, veh_orig_date, parcels)
        #2.remove capacity in veh_cap
        self.remove_from_veh_cap_dic(veh_orig, veh_dest, veh_orig_date, veh_dest_date, total_weight)
        
     
    def loading_request(self, v):
        #1.	for each parcel in veh_parcel_assignment
        #    load parcel to vehicle
        #    remove from rtd_demand
        #    if next dest not final dest, add to en_route_demand and add enroute key to parcel
        assignment_exists = False
        if v.orig_gh in self.veh_parcel_assignment:
            if v.dest_gh in self.veh_parcel_assignment[v.orig_gh]:
                if v.orig_date in self.veh_parcel_assignment[v.orig_gh][v.dest_gh]:
                    assignment_exists = True
        
        if assignment_exists:
            for p in self.veh_parcel_assignment[v.orig_gh][v.dest_gh][v.orig_date]:
                v.load_parcel(p)
                # print(p.weight, v.load)
                self.remove_from_rtd_demand(v.orig_gh, p.dest_gh, p.dest_date, [p])
                if v.dest_gh != p.dest_gh:
                    self.add_to_en_route_demand(v.dest_gh, p.dest_gh, v.dest_date, p.dest_date, [p])
                    p.en_route_key = (v.dest_gh, p.dest_gh, v.dest_date, p.dest_date)
            #2. remove parcels from veh_parcel_assignment
            self.remove_from_veh_parcel_assignment(v.orig_gh, v.dest_gh, v.orig_date, v.loaded_parcels)
        #3.	remove (veh_cap - veh_load) from veh_cap
        if round(v.load,3) > round(v.capacity,3):
            raise
        self.remove_from_veh_cap_dic(v.orig_gh, v.dest_gh, v.orig_date, v.dest_date, v.capacity - v.load)
        #4.	remove from dispatch_vehicles
        for input_id in v.dispatch_vehicles:
            for cap in v.dispatch_vehicles[input_id]:
                self.remove_from_dispatch_vehicles(v.orig_gh, v.dest_gh, v.orig_date, input_id, cap)
                
        #5.	send vehicle to dest
        v.move_to_next_destination()




    def unloading_request(self, v):
        for p in v.loaded_parcels:
            #if final dest, call record statistics
            if p.dest_gh == v.dest_gh:
                self.main.record_statistics.notify_parcel_reached_final_destination(p)
                continue
            #1.	remove parcel from en_route_demand and remove key of en_route demand from parcel
            self.remove_from_en_route_demand(p.en_route_key[0], p.en_route_key[1], p.en_route_key[2], p.en_route_key[3], [p])
            p.en_route_key = None
            #2. add parcel to rtd_demand
            self.add_to_rtd_demand(v.dest_gh, p.dest_gh, p.dest_date, [p])
        #3. call notify_vehicle_reached_final_destination in record statistics
        self.main.record_statistics.notify_vehicle_reached_final_destination(v)
        
        
        
    def schedule_planned_vehicles(self):
        df_vehicles = self.main.pd.read_csv(self.main.inputs.vehicles_file_name)
        for index, row in df_vehicles.iterrows():
            orig_date = self.main.pd.to_datetime(row['orig_date'])
            orig_gh = row['orig_gh']
            dest_gh = row['dest_gh']
            capacity = float(row['capacity'])
            input_id = row['input_id']
            self.schedule_vehicle(input_id, orig_gh, dest_gh,orig_date, capacity)
        





if __name__ == "__main__":
    print('imported main in router code')
    import main 
    main.run()

    
    
    
    
    
    
    
    
    
    

    
    
    