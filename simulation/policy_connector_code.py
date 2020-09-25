#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug  3 20:36:16 2020

@author: Moussa
"""



class PolicyConnector:
    def __init__(self, main_object):
        self.main = main_object
        self.first_period = True
        self.pre_decision_costs = [] #[costs at beginnings of each period for t = 0, …, T]
        self.pre_decision_states = [] #[start_of_period_states for t = 0, …, T]
        self.cost_of_actions = [] #[cost of actions from t = 0, … , T-1]
        self.post_decision_states = [] #[pd_state for t = 0, …, T-1]
        self.pre_decision_states_values = [] #[value of pre decision states for t = 0, …, T]
        self.post_decision_states_values = [] #[value of post decision states for t = 0, …, T-1]        
        self.main.env.process(self.schedule_intervals())
        
   
    
    
    def schedule_intervals(self):
        if self.first_period:
            delay = 0
            self.first_period = False
        else:
            delay = self.main.inputs.time_discretization_factor
        self.main.simpy.events.NORMAL = 3
        event = self.main.simpy.events.Timeout(self.main.env, delay)
        self.main.simpy.events.NORMAL = 1
        yield event
        self.interval_algorithm()
        if self.main.env.now < self.main.inputs.simulation_end_time:
            self.main.env.process(self.schedule_intervals())
            
            
# 	
# 	4.	call policy.new_period and get actions
# 	5.	record cost_of_action, pd_state -> get cost of actions after the actions are executed?
# 	6.	execute actions

            
    
    def interval_algorithm(self):
        # print('interval ', self.main.convert_to_date(self.main.env.now))
        # 1. if not itinerary, self.discard_late_parcels()
        if self.main.inputs.policy_name != 'itinerary':
            self.discard_late_parcels()
            current_cost = self.main.record_statistics.total_cost
        else:
            current_cost = self.main.record_statistics.created_vehicles_cost
        # 2.	calculate_state_variables
        d, v, tensor_position_to_rtd_parcels = self.calculate_state_variables()
        # 3.	record start_of_period_costs, start_of_period_state
        self.pre_decision_costs.append(current_cost)
        self.pre_decision_states.append(self.main.np.array(d))
        # 4.	4.	if itinerary return, if period == T, calculate_value_of_states, return
        current_period = self.main.env.now / self.main.inputs.time_discretization_factor
        if current_period == self.main.inputs.simulation_end_time / self.main.inputs.time_discretization_factor:
            self.calculate_value_of_states()
            return
        if self.main.inputs.policy_name == 'itinerary': 
            return
        # 5. call policy.get_action
        vehicles, assignments, cost_of_action, d_pd =  self.main.policy.get_action(d, v, current_period)
        # 6.	record cost_of_action, pd_state 
        self.cost_of_actions.append(cost_of_action)
        self.post_decision_states.append(d_pd)
        # 7.	execute actions
        self.execute_action(vehicles, assignments, tensor_position_to_rtd_parcels)
    
    
    
    def calculate_value_of_states(self):
        final_cost = self.pre_decision_costs[-1]
        for t in range(len(self.post_decision_states)):
            value = final_cost - self.pre_decision_costs[t] - self.cost_of_actions[t]
            self.post_decision_states_values.append(value)
        for t in range(len(self.pre_decision_states)):
            value = final_cost - self.pre_decision_costs[t]
            self.pre_decision_states_values.append(value)

        
        
        
    
    
        
    def discard_late_parcels(self):
        a_dic = {} 
        #1.	go through rtd parcels, the ones that would be late now even with direct routing, remove them from rtd_parcels
        for orig_gh in self.main.router.rtd_demand:
            for dest_gh in self.main.router.rtd_demand[orig_gh]:
                tt = self.main.inputs.travel_times[orig_gh][dest_gh]
                for due_date in self.main.router.rtd_demand[orig_gh][dest_gh]:
                    slack = self.main.convert_to_simulation_time(due_date) - self.main.env.now
                    if slack < tt:
                        if orig_gh not in a_dic:
                            a_dic[orig_gh] = {}
                        if dest_gh not in a_dic[orig_gh]:
                            a_dic[orig_gh][dest_gh] = {}
                        a_dic[orig_gh][dest_gh][due_date] = []
                        for p in self.main.router.rtd_demand[orig_gh][dest_gh][due_date]:
                            a_dic[orig_gh][dest_gh][due_date].append(p)
        for orig_gh in a_dic:
            for dest_gh in a_dic[orig_gh]:
                for due_date in a_dic[orig_gh][dest_gh]:
                    self.main.router.remove_from_rtd_demand(orig_gh, dest_gh, due_date, a_dic[orig_gh][dest_gh][due_date])
        #2. record_statistics.notify_parcel_discarded
        self.main.record_statistics.notify_late_parcels_discarded(a_dic)
        
    
    
    def execute_action(self, vehicles, assignments, tensor_position_to_rtd_parcels):
        current_date = self.main.convert_to_date(self.main.env.now)
        # 1. call router.schedule_vehicle for vehicles schedule_vehicle(self,input_id, orig_gh, dest_gh, orig_date, capacity):
        for key in vehicles:
            orig_gh = self.main.inputs.index_to_location[key[0]]
            dest_gh = self.main.inputs.index_to_location[key[1]]
            self.main.router.schedule_vehicle(-1, orig_gh, dest_gh, current_date, vehicles[key])
        # 2. call router.assign_parcels_to_vehicle for assignments assign_parcels_to_vehicle(self, parcels, veh_orig, veh_dest, veh_orig_date):
        for tensor_position in assignments:
            if tensor_position not in tensor_position_to_rtd_parcels:
                print("error in policy_connector.execute_action")
                raise
            veh_orig = self.main.inputs.index_to_location[tensor_position[0]]
            veh_dest = self.main.inputs.index_to_location[assignments[tensor_position]]
            self.main.router.assign_parcels_to_vehicle(tensor_position_to_rtd_parcels[tensor_position], veh_orig, veh_dest, current_date)
            

        
        
        
    
    
    def calculate_state_variables(self):
        #1.	from the environment make d tensor based on descretization period 
        #for the parcels in rtd, add them to position_to_parcels
        n_locations = len(self.main.inputs.location_to_index)
        n_dates = 1 + self.main.math.ceil((self.main.inputs.simulation_end_date - self.main.inputs.simulation_start_date).total_seconds() * 1000.0 / self.main.inputs.time_discretization_factor)
        d = self.main.np.zeros((n_locations, n_dates, n_locations, n_dates))
        v = self.main.np.zeros((n_locations, n_dates, n_locations, n_dates))
        # 1.	add future_demand to d {ogh: {dgh: {od: {dd: mean}}}
        for orig_gh in self.main.router.future_demand:
            for dest_gh in self.main.router.future_demand[orig_gh]:
                for orig_date in self.main.router.future_demand[orig_gh][dest_gh]:
                    for dest_date in self.main.router.future_demand[orig_gh][dest_gh][orig_date]:
                        t1, t2 = self.discretize_demand_dates(orig_date, dest_date)
                        l1 = self.main.inputs.location_to_index[orig_gh]
                        l2 = self.main.inputs.location_to_index[dest_gh]
                        tensor_position = (l1, t1, l2, t2)
                        d[tensor_position] = d[tensor_position] + self.main.router.future_demand[orig_gh][dest_gh][orig_date][dest_date]
                       
        # 2.	add en_route demand to d self.en_route_demand = {} #{ogh: {dgh: {od: {dd: [parcels]}}}
        for orig_gh in self.main.router.en_route_demand:
            for dest_gh in self.main.router.en_route_demand[orig_gh]:
                for orig_date in self.main.router.en_route_demand[orig_gh][dest_gh]:
                    for dest_date in self.main.router.en_route_demand[orig_gh][dest_gh][orig_date]:
                        t1, t2 = self.discretize_demand_dates(orig_date, dest_date)
                        l1 = self.main.inputs.location_to_index[orig_gh]
                        l2 = self.main.inputs.location_to_index[dest_gh]
                        tensor_position = (l1, t1, l2, t2)
                        total_weight = sum(p.weight for p in self.main.router.en_route_demand[orig_gh][dest_gh][orig_date][dest_date])
                        d[tensor_position] = d[tensor_position] + total_weight
                         
        # 3.	add rtd_demand to d {ogh: {dgh: {dd: [parcels]}}}    
        # 4.	add_rtd_demand parcels to tensor_position_to_rtd_parcels
        tensor_position_to_rtd_parcels = {}
        orig_date = self.main.convert_to_date(self.main.env.now)   
        for orig_gh in self.main.router.rtd_demand:
            for dest_gh in self.main.router.rtd_demand[orig_gh]:
                for dest_date in self.main.router.rtd_demand[orig_gh][dest_gh]:
                    t1, t2 = self.discretize_demand_dates(orig_date, dest_date)
                    l1 = self.main.inputs.location_to_index[orig_gh]
                    l2 = self.main.inputs.location_to_index[dest_gh]
                    tensor_position = (l1, t1, l2, t2)
                    total_weight = sum(p.weight for p in self.main.router.rtd_demand[orig_gh][dest_gh][dest_date])
                    d[tensor_position] = d[tensor_position] + total_weight
                    if tensor_position not in tensor_position_to_rtd_parcels:
                        tensor_position_to_rtd_parcels[tensor_position] = [] 
                    tensor_position_to_rtd_parcels[tensor_position] = self.main.router.rtd_demand[orig_gh][dest_gh][dest_date] + tensor_position_to_rtd_parcels[tensor_position]
        
        
        #5.	create v tensor from veh capacity - #{ogh: {dgh: {od: {dd: capacity}}}
        for orig_gh in self.main.router.veh_cap:
            for dest_gh in self.main.router.veh_cap[orig_gh]:
                for orig_date in self.main.router.veh_cap[orig_gh][dest_gh]:
                    for dest_date in self.main.router.veh_cap[orig_gh][dest_gh][orig_date]:
                        t1, t2 = self.discretize_vehicle_dates(orig_date, dest_date)
                        l1 = self.main.inputs.location_to_index[orig_gh]
                        l2 = self.main.inputs.location_to_index[dest_gh]
                        tensor_position = (l1, t1, l2, t2)
                        v[tensor_position] = v[tensor_position] + self.main.router.veh_cap[orig_gh][dest_gh][orig_date][dest_date]
        
        #6.	return d, tensor_position_to_rtd_parcels
        return d, v, tensor_position_to_rtd_parcels
       
        
        
    def discretize_vehicle_dates(self, orig_date, dest_date):
        #orig_date: round down, dest_date: round up
        t1 = (orig_date - self.main.inputs.simulation_start_date).total_seconds() * 1000.0
        t1 = self.main.math.floor(t1 / self.main.inputs.time_discretization_factor) 
        t2 = (dest_date - self.main.inputs.simulation_start_date).total_seconds() * 1000.0
        t2 = self.main.math.ceil(t2 / self.main.inputs.time_discretization_factor) 
        return t1, t2
        
        
        
    def discretize_demand_dates(self, orig_date, dest_date):
        #1.	orig date: round up, dest date: round down
        t1 = (orig_date - self.main.inputs.simulation_start_date).total_seconds() * 1000.0
        t1 = self.main.math.ceil(t1 / self.main.inputs.time_discretization_factor) 
        t2 = (dest_date - self.main.inputs.simulation_start_date).total_seconds() * 1000.0
        t2 = self.main.math.floor(t2 / self.main.inputs.time_discretization_factor) 
        return t1, t2



if __name__ == "__main__":
    print('main imported in direct routing policy')
    import main as m
    m.run()

    
    
    
    
    
    
