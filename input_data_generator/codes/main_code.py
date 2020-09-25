



class Main(): 
    def __init__(self):
        #imports
        import random as r
        self.random = r
        import numpy as np
        self.np = np
        ##setting random seed
        r.seed(a=7)
        np.random.seed(7)
        
        import os as o
        self.os = o
        import pandas as pd
        self.pd = pd
        import datetime as dt
        self.datetime = dt
        import gurobipy as gbpy
        self.gp = gbpy
        import creating_demand_code as cd
        self.creating_demand_code = cd
        import creating_vehicles_code as cv
        self.creating_vehicles_code = cv
        
        #input variables
        self.travel_time_file_path = "../data/synthetic_travel_times.csv"
        self.ghs_file_path = "../data/synthetic_ghs.csv"
        self.vehicle_costs_file_path = '../data/synthetic_vehicle_costs.csv'
        self.demand_start_date = self.datetime.datetime(2019, 3, 27)
        self.demand_end_date = self.datetime.datetime(2019, 3, 27, 10)
        self.number_of_demands = 50
        self.mean_of_demand_mean = 60
        self.std_of_demand_mean = 20
        self.maximum_demand_slack = 10 * 60 * 60 * 1000
        self.time_descretization = 1 * 60 * 60 * 1000
        self.optimization_little_m = 0.001
        self.optimization_iteration = 1
        self.number_of_instances = 5
        self.number_of_demand_realizations = 0
        
        #input functions
        self.travel_times_dic = {}
        self.ghs = [] 
        self.read_travel_times()
        self.read_ghs()
        self.vehicle_costs_dic = {}  #first key: orig_gh, second key: dest_gh, third key: required_capacity, value = [cost, dictionary of vehicle type and number of vehicles]
        self.read_vehicle_costs()
        
        #creting demand, vehicles, files
        self.root_function()
        
        
    def read_travel_times(self):
        df = self.pd.read_csv(self.travel_time_file_path)
        for index, row in df.iterrows():
            orig_gh = row.orig_gh
            dest_gh = row.dest_gh
            tt = float(row.travel_time_ms)
            if orig_gh not in self.travel_times_dic:
                self.travel_times_dic[orig_gh] = {}
            self.travel_times_dic[orig_gh][dest_gh] = tt
            
    def get_travel_time(self, orig_gh, dest_gh):
        if orig_gh not in self.travel_times_dic:
            return None
        if dest_gh not in self.travel_times_dic[orig_gh]:
            return None
        return self.travel_times_dic[orig_gh][dest_gh]
    
    def read_ghs(self):
        df = self.pd.read_csv(self.ghs_file_path)
        for index, row in df.iterrows():
            self.ghs.append(row.site_code)
    
    def read_vehicle_costs(self):
        df = self.pd.read_csv(self.vehicle_costs_file_path)
        for index, row in df.iterrows():
            if row.orig_gh not in self.vehicle_costs_dic:
                self.vehicle_costs_dic[row.orig_gh] = {}
            if row.dest_gh not in self.vehicle_costs_dic[row.orig_gh]:
                self.vehicle_costs_dic[row.orig_gh][row.dest_gh] = {}
            a_dic = {}
            for item in row.vehicles.split("&"):
                veh_type, num_vehicles = item.split(":")
                a_dic[float(veh_type)] = float(num_vehicles)
            self.vehicle_costs_dic[row.orig_gh][row.dest_gh][row.required_capacity] = [row.cost, a_dic]
            
    
    def get_minimum_cost_vehicle(self, orig_gh, dest_gh, needed_capacity): #returns cost and the total cap of vehicle
        if needed_capacity == 0:
            return 0,0
        req_cap_list = list(self.vehicle_costs_dic[orig_gh][dest_gh].keys())
        req_cap_list.sort()
        for cap in req_cap_list:
            selected_cap = cap
            if needed_capacity <= selected_cap:
                break
        if selected_cap == req_cap_list[-1]:
            print('maximum capacity reached in getting the cost of vehicle')
        cost, a_dic = self.vehicle_costs_dic[orig_gh][dest_gh][selected_cap]
        total_cap = 0
        for veh_type in a_dic:
            total_cap += veh_type * a_dic[veh_type]
        return cost, total_cap
    
                
                
    
    
    
    
    def root_function(self):
        for i in range(self.number_of_instances):
            folder_name = 'instance' + str(i) + "/"
            try:
                self.os.mkdir('../output/' + folder_name)
            except:
                pass
            d = self.creating_demand_code.CreateDemand(self)
            v = self.creating_vehicles_code.CreateVehicles(self, d.created_demand)
            #self.total_cost, self.vehicles, self.itineraries, self.avg_utilization
            #
            print('=====')
            print(v.total_cost)
            print(v.avg_utilization)
            output_list = [] 
            for i in range(len(d.created_demand)):
                demand = d.created_demand[i]
                output_list.append((i, demand[0],demand[1],demand[2],demand[3],demand[4]))
            df = self.pd.DataFrame(output_list, columns = ["input_id", "orig_gh", "orig_date", "dest_gh", "dest_date", "weight"])
            df.to_csv('../output/' + folder_name + 'original_demand.csv', index = False)
            #020WD_2019-03-28 23:00:00_020WG&020WG_2019-03-29 00:45:00_020W
            output_list = [] 
            for input_id in range(len(d.created_demand)):
                itinerary_string = ""
                itinerary = v.itineraries[input_id]
                itinerary.sort(key=lambda x:x[1])
                for item in itinerary:
                    itinerary_string += item[0] + "_" + str(item[1]) + "_" + item[2] + "&"
                itinerary_string = itinerary_string[:-1]
                output_list.append((input_id, itinerary_string))
            df = self.pd.DataFrame(output_list, columns = ["input_id", "itinerary"])
            df.to_csv('../output/' + folder_name + 'itineraries.csv', index = False)
            output_list = [] 
            n = 0
            for arc_key in v.vehicles:
                output_list.append((n, arc_key[0], arc_key[1],arc_key[2], v.vehicles[arc_key]))
                n+=1
            df = self.pd.DataFrame(output_list, columns = ["input_id", "orig_gh", "orig_date", "dest_gh", "capacity"])
            df.to_csv('../output/' + folder_name + 'vehicles.csv', index = False)
            
            for j in range(self.number_of_demand_realizations):
                d = self.creating_demand_code.CreateDemand(self)
                output_list = [] 
                for i in range(len(d.created_demand)):
                    demand = d.created_demand[i]
                    output_list.append((i, demand[0],demand[1],demand[2],demand[3],demand[4]))
                df = self.pd.DataFrame(output_list, columns = ["input_id", "orig_gh", "orig_date", "dest_gh", "dest_date", "weight"])
                df.to_csv('../output/' + folder_name + 'demand_realization_' + str(j) + '.csv', index = False)
            
        
            
            
        
        
        







import time
t0 = time.time()
Main()
print('code took %s' %(time.time() - t0))
















