#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 21:37:50 2020

@author: Moussa
"""

class RecordStatistics():
    def __init__(self, main_object):
        self.main_object = main_object
        #statistics parameters
        self.total_cost = 0
        self.created_vehicles_cost = 0
        #self.vehicle_cost_not_found = 0
        self.total_p_load_created = 0
        self.total_v_created = 0
        self.total_policy_v_created = 0
        self.total_p_load_reached_destination = 0
        self.total_load_travel_time = 0
        self.total_capacity_travel_time = 0
        self.vehicle_utilizations = [] #utilizations of vehicles
        self.main_object.env.process(self.before_end_of_simulation())
        
    
    
    def notify_vehicle_scheduled(self, orig_gh, dest_gh, capacity):
        self.total_cost += self.main_object.inputs.vehicle_costs[orig_gh][dest_gh][capacity][0]
        

    
    def notify_parcel_created(self, p):
        self.total_p_load_created = round(self.total_p_load_created + p.weight,3)
        
        
    def notify_vehicle_created(self, v):
        for input_id in v.dispatch_vehicles:
            self.total_v_created += len(v.dispatch_vehicles[input_id])
            for cap in v.dispatch_vehicles[input_id]:
                self.created_vehicles_cost += self.main_object.inputs.vehicle_costs[v.orig_gh][v.dest_gh][cap][0]
            if input_id < 0:
                self.total_policy_v_created += len(v.dispatch_vehicles[input_id])
            
        
        
        
    def notify_parcel_reached_final_destination(self, p):
        self.total_p_load_reached_destination = round(self.total_p_load_reached_destination + p.weight,3)
        if self.main_object.env.now > p.dest_time:
            raise
        
    def notify_vehicle_reached_final_destination(self, v):
        tt = v.dest_time - v.orig_time
        self.total_load_travel_time += v.load * tt
        self.total_capacity_travel_time += v.capacity * tt
        self.vehicle_utilizations.append(v.load/v.capacity)

    

    def notify_late_parcels_discarded(self, discard_dic):
        for orig_gh in discard_dic:
            for dest_gh in discard_dic[orig_gh]:
                total_weight = 0
                for due_date in discard_dic[orig_gh][dest_gh]:
                    total_weight += sum(p.weight for p in discard_dic[orig_gh][dest_gh][due_date])
                cost, cap = self.main_object.inputs.get_minimum_cost_vehicle(orig_gh, dest_gh, total_weight)
                self.total_cost += cost
        
                
    

    def before_end_of_simulation(self):
        delay = self.main_object.convert_to_simulation_time(self.main_object.inputs.simulation_end_date)
        self.main_object.simpy.events.NORMAL = 5
        event = self.main_object.simpy.events.Timeout(self.main_object.env, delay)
        self.main_object.simpy.events.NORMAL = 1
        yield event
        print("+++++++++++++++++++++\n+++++++++++++++++++++\n+++++++++++++++++++++")
        print("parcels created: %s" % (self.total_p_load_created))
        print("parcels reaching destination %s" % (self.total_p_load_reached_destination))
        print("number of vehicles created: %s" % (self.total_v_created))
        print("number of vehicles created by policy: %s" %(self.total_policy_v_created))
        try:
            print("total utilization: %s" % (self.total_load_travel_time / self.total_capacity_travel_time))
            print("average vehicle utilization %s" % (sum(self.vehicle_utilizations) / len(self.vehicle_utilizations)))
        except:
            print('couldnt get utilization')
        print("total cost %s" % (round(self.total_cost)))
        
        
       
 

if __name__ == "__main__":
    # print('main imported to record statistics')
    import main as m
    m.run()

    

       
        
       