#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 19:59:44 2020

@author: Moussa
"""


class Inputs():
    def __init__(self, main_object):
        self.main = main_object
        self.travel_times = {}
        self.vehicle_costs = {}
        self.lowest_cost_vehicle_costs_matrix = None
        self.travel_times_matrix = None
        self.location_to_index = {}
        self.index_to_location = {} 
        self.initialize_parameters()
        self.simulation_end_time = (self.simulation_end_date-self.simulation_start_date).total_seconds()*1000.0
        self.initialize_hubs()
        self.initialize_travel_times()
        self.initialize_vehicle_costs()
        self.initialize_costs_matrix()
        
        
    def initialize_parameters(self):
        ##input files
        '''
        self.demand_file_name = "../input_data/20191025_c2_simpy_demand_log.csv"
        #self.hubs_file_name = "../input_data/synthetic_ghs.csv"
        self.vehicles_file_name = "../input_data/20191025_c2_simpy_vehicles.csv"
        self.travel_times_file_name = "../input_data/20191025_c2_simpy_travel_times_based_on_incompatbile_vehicles.csv"
        self.vehicle_costs_file_name = "../input_data/20191025_c2_simpy_vehicle_costs_with_incompatible_vehicles.csv"
        self.itineraries_file_name = "../input_data/20191025_c2_simpy_itineraries.csv"
        self.simulation_start_date = self.main.datetime.datetime(2019,3,26,0,0,0)
        self.simulation_end_date = self.main.datetime.datetime(2019,3,31,0,0,0)
        '''
        self.demand_file_name = None
        self.vehicles_file_name = None
        self.itineraries_file_name = None       # "../input_data/itineraries.csv"
        self.hubs_file_name = "../input_data/synthetic_ghs.csv"
        self.travel_times_file_name = "../input_data/synthetic_travel_times.csv"
        self.vehicle_costs_file_name = "../input_data/synthetic_vehicle_costs.csv"
        self.policy_file_name = "linear_regression_policy_code"
        
        ##input parameters
        self.simulation_start_date = self.main.datetime.datetime(2019,3,27,0,0,0)
        self.simulation_end_date = self.main.datetime.datetime(2019,3,27,10,0,0)
        self.time_discretization_factor = 1*60*60*1000
        self.policy_name = None
        
        
        
        
        
    def initialize_costs_matrix(self):
        location_indices = list(self.index_to_location.keys())
        self.lowest_cost_vehicle_costs_matrix = self.main.np.zeros((len(location_indices),len(location_indices)))
        
        for l1 in location_indices:
            for l2 in location_indices:
                if l1 != l2:
                    #print(self.vehicle_costs[self.index_to_location[l1]][self.index_to_location[l2]])
                    cap = min(list(self.vehicle_costs[self.index_to_location[l1]][self.index_to_location[l2]].keys()))
                    
                    self.lowest_cost_vehicle_costs_matrix[(l1, l2)] = self.vehicle_costs[self.index_to_location[l1]][self.index_to_location[l2]][cap][0]
        
    def initialize_travel_times(self):
        df = self.main.pd.read_csv(self.travel_times_file_name)
        for index, row in df.iterrows():
            orig_gh = row['orig_gh']
            dest_gh = row['dest_gh']
            travel_time = row['travel_time_ms']
            if orig_gh not in self.travel_times:
                self.travel_times[orig_gh] = {}
            if dest_gh in self.travel_times[orig_gh]:
                print('Error in router: multiple travel times for same od pair! ')
            self.travel_times[orig_gh][dest_gh] = travel_time
        n_locations = len(list(self.travel_times.keys()))
        self.travel_times_matrix = self.main.np.zeros((n_locations, n_locations))
        for l1 in range(n_locations):
            for l2 in range(n_locations):
                if l1 != l2:
                    tt = self.travel_times[self.index_to_location[l1]][self.index_to_location[l2]]
                    self.travel_times_matrix[(l1, l2)] = tt
        
            
        
    
    def initialize_vehicle_costs(self):
        #t0 = self.main.time.time()
        df = self.main.pd.read_csv(self.vehicle_costs_file_name)
        for index, row in df.iterrows():
            if row.orig_gh not in self.vehicle_costs:
                self.vehicle_costs[row.orig_gh] = {}
            if row.dest_gh not in self.vehicle_costs[row.orig_gh]:
                self.vehicle_costs[row.orig_gh][row.dest_gh] = {}
            vs = row.vehicles.split("&")
            a_dic = {}
            for item in vs:
                vehicle_cap, n_vehicles = item.split(":")
                a_dic[float(vehicle_cap)] = float(n_vehicles)
            self.vehicle_costs[row.orig_gh][row.dest_gh][row.required_capacity] = [row.cost, a_dic]
        
            


    def initialize_hubs(self):
        df = self.main.pd.read_csv(self.hubs_file_name)
        hub_list = list(df.site_code)
        hub_list.sort()
        for i in range(len(hub_list)):
            self.location_to_index[hub_list[i]] = i
            self.index_to_location[i] = hub_list[i]
        
        
        
    def get_minimum_cost_vehicle(self, orig_gh, dest_gh, needed_capacity): #returns cost and the total cap of vehicle
        if needed_capacity == 0:
            return 0,0
        req_cap_list = list(self.vehicle_costs[orig_gh][dest_gh].keys())
        req_cap_list.sort()
        for cap in req_cap_list:
            selected_cap = cap
            if needed_capacity <= selected_cap:
                break
        if selected_cap == req_cap_list[-1]:
            print('maximum capacity reached in getting the cost of vehicle')
        cost, a_dic = self.vehicle_costs[orig_gh][dest_gh][selected_cap]
        total_cap = 0
        for veh_type in a_dic:
            total_cap += veh_type * a_dic[veh_type]
        return cost, total_cap

        




if __name__ == '__main__':
    print('main imported to inputs code')
    import main as m
    main = m.Main()
    main.initialize_inputs()
    main.run_simulation()
    
    
    