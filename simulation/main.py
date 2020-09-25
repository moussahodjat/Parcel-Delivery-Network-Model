# -*- coding: utf-8 -*-


class Main():
    def __init__(self):
        #python imports 
        import pandas as pd
        self.pd = pd        
        import datetime as dt
        self.datetime = dt
        import time as t
        self.time = t
        import simpy as s
        self.simpy = s
        import numpy as n
        self.np = n
        self.np.random.seed(7)
        import math as m
        self.math = m
        import importlib as il
        self.importlib = il
        import gurobipy as gbpy
        self.gp = gbpy
        #code imports
        import demand_generator_code as dgc
        self.demand_generator_code = dgc
        import parcel_code as pc
        self.parcel_code = pc
        import router_code as rc
        self.router_code = rc
        import hub_code as hc
        self.hub_code = hc
        import vehicle_code as vc
        self.vehicle_code = vc
        import itinerary_policy_code as ipc
        self.itinerary_policy_code = ipc
        import record_statistics_code as rsc
        self.record_statistics_code = rsc
        import inputs_code as ic
        self.inputs_code = ic
        import policy_connector_code as pcc
        self.policy_connector_code = pcc
    def initialize_inputs(self):
        #initializing inputs
        # t0 =  self.time.time()
        self.inputs = self.inputs_code.Inputs(self)
        # print('initializing inputs took %s ' % (self.time.time() - t0))
        # print("____________")
    
    def run_simulation(self, betas = None):
        # start_time = self.time.time()
        self.env = self.simpy.Environment()
        #initialize record statistics object
        self.record_statistics = self.record_statistics_code.RecordStatistics(self)
        #initializing router 
        self.router = self.router_code.Router(self)
        #initializing demand generator
        self.demand_generator = self.demand_generator_code.DemandGenerator(self)
        #initializing policy and policy connector 
        self.policy_connector = self.policy_connector_code.PolicyConnector(self)
        if self.inputs.policy_name == "itinerary":
            self.itinerary_policy = self.itinerary_policy_code.ItineraryPolicy(self)
        else:
            pfn = self.importlib.import_module(self.inputs.policy_file_name) 
            self.policy = pfn.Policy(self)
            self.policy.betas = betas
        
        self.env.run()
        # print("+++++++++++++++++++++\n+++++++++++++++++++++\n+++++++++++++++++++++")
        # print("total execution time %s seconds"  % (self.time.time() - start_time))

    
    def convert_to_simulation_time(self, date):
        return (date - self.inputs.simulation_start_date).total_seconds()*1000
    def convert_to_date(self, simulation_time):
        return self.inputs.simulation_start_date + self.datetime.timedelta(milliseconds = simulation_time)
    
    
        






import numpy
import time
import multiprocessing
import pandas
import concurrent.futures
def update_betas(main, previous_betas, alpha):
    for t in range(24):
        pd_s = main.policy.pd_states[t]
        actual = main.policy.state_values[t]
        pred = numpy.sum(numpy.multiply(pd_s, previous_betas))
        error = pred - actual
        step_size = alpha*error
        betas = previous_betas - step_size * pd_s
    return betas



def one_iteration(demand_num, main_dic, betas, veh_file_name, demand_file_name):
    main = Main()
    main.initialize_inputs()
    main.inputs.vehicles_file_name = veh_file_name 
    main.inputs.demand_file_name = demand_file_name 
    main.run_simulation(betas)
    main_dic[demand_num] = main



def root_function():
    t0 = time.time()
    alpha = 0.1
    different_demand_iterations = 10
    n_beta_updates = 10
    veh_file_name = '../../input_data_generator/output/instance0/vehicles.csv'
    betas = numpy.zeros((5,25,5,25))
    n_parallels = multiprocessing.cpu_count()

    
    for i in range(1):
        main = Main()
        main.initialize_inputs()
        main.inputs.vehicles_file_name = veh_file_name 
        main.inputs.demand_file_name = '../../input_data_generator/output/instance0/original_demand.csv' 
        main.run_simulation(betas)
        print(i, main.record_statistics.total_policy_v_created, main.record_statistics.total_cost)    
        print("------------")
        demand_num = 0
        while demand_num < different_demand_iterations:
            processes = []
            manager = multiprocessing.Manager()
            main_dic = manager.dict()
            for _ in range(n_parallels):
                if demand_num < different_demand_iterations:
                    p = multiprocessing.Process(target = one_iteration, args = (demand_num, main_dic, betas, veh_file_name, '../../input_data_generator/output/instance0/demand_realization_'+ str(demand_num) + '.csv'))
                    processes.append(p)
                    p.start()
                    
                    demand_num += 1
                    
                else:
                    break
            print(len(main_dic), "----------")
            for p in processes:
                p.join()
                
            print(main_dic.keys())
            # for _ in range(n_beta_updates):
            #     for main in main_list:
            #         betas = update_betas(main, betas, alpha)
            
       
    print('total time: %s' %(time.time() - t0))
 







if __name__ == '__main__':
    root_function()
    run()
    t0 = time.time(); 
    run()
    with concurrent.futures.ProcessPoolExecutor() as executor:
         processes = [] 
         for i in range(5):
             executor.submit(run,i)
        
    
    print(time.time() - t0)














