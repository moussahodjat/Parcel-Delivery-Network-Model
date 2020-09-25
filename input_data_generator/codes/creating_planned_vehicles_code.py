#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#import os
# import gurobipy as gp
# from gurobipy import GRB
# file_directories = os.listdir("../output")
# file_directories = ["../output/" + name for name in file_directories]
# file_directories.remove("../output/.DS_Store")



class Node:
    def __init__(self):
        self.date = None
        self.hub = None
        self.input_arcs = [] 
        self.output_arcs = [] 
        # self.input_arc_variables = {}
        # self.output_arc_variables = {}



class Arc:
    def __init__(self):
        #self.cost = None
        self.orig_node = None
        self.dest_node = None
        self.flow_variables = {}
        self.binary_variable = None
        


class CreateVehicles:
    def __init__(self, main_object, demand_list):
        self.main = main_object
        self.demand_list = demand_list
        self.nodes = {} #first key: hub, second key: date, value: node
        self.arcs = {} #first_key: orig_hub, second_key: orig_date, third_key: dest_hub, fourth_key: dest_date, value: arc
        self.create_time_space_network()
        self.total_cost, self.vehicles, self.itineraries, self.avg_utilization = self.create_vehicles()
        
        
    def add_node_to_dic(self, n): #returns true if node is already in the dic, false otherwise
        if n.hub not in self.nodes:
            self.nodes[n.hub] = {}
        if n.date not in self.nodes[n.hub]:
            self.nodes[n.hub][n.date] = n
        else:
            return True
        return False
    
    
    def add_arc_to_dic(self, a): #returns true if arc already in the dic, false otw
        if a.orig_node.hub not in self.arcs:
            self.arcs[a.orig_node.hub] = {}
        if a.orig_node.date not in self.arcs[a.orig_node.hub]:
            self.arcs[a.orig_node.hub][a.orig_node.date] = {}
        if a.dest_node.hub not in self.arcs[a.orig_node.hub][a.orig_node.date]:
            self.arcs[a.orig_node.hub][a.orig_node.date][a.dest_node.hub] = {}
        if a.dest_node.date in self.arcs[a.orig_node.hub][a.orig_node.date][a.dest_node.hub]:
            return True
        else:
            self.arcs[a.orig_node.hub][a.orig_node.date][a.dest_node.hub][a.dest_node.date] = a
            return False
                     
      
        
    def create_time_space_network(self):
        nodes_to_be_processed = []
        #adding origin of demands to nodes
        for demand in self.demand_list:
            n = self.main.creating_vehicles_code.Node()
            n.date = demand[1]
            n.hub = demand[0]
            if not self.add_node_to_dic(n):
                nodes_to_be_processed.append(n)
            n = self.main.creating_vehicles_code.Node()
            n.date = demand[3]
            n.hub = demand[2]
            if not self.add_node_to_dic(n):
                nodes_to_be_processed.append(n)
        node_index = 0
        arc_index = 0
        while node_index < len(nodes_to_be_processed):
            n = nodes_to_be_processed[node_index]
            for gh in self.main.ghs:
                if gh != n.hub: 
                    new_node = self.main.creating_vehicles_code.Node()
                    tt = self.main.get_travel_time(n.hub, gh)
                    new_node.date = n.date + self.main.datetime.timedelta(milliseconds = tt)
                    new_node.hub = gh
                    if new_node.date <= self.main.demand_end_date:
                        if not self.add_node_to_dic(new_node):
                            nodes_to_be_processed.append(new_node)
                        else:
                            new_node = self.nodes[new_node.hub][new_node.date]
                        #adding arc
                        a = self.main.creating_vehicles_code.Arc()
                        a.orig_node = n
                        a.dest_node = new_node
                        #arc_cost, cap = self.main.get_minimum_cost_vehicle(n.hub, new_node.hub, 0)
                        #a.cost = arc_cost
                        if self.add_arc_to_dic(a):
                            raise
                        else:
                            arc_index += 1
                            a.orig_node.output_arcs.append(a)
                            a.dest_node.input_arcs.append(a)
            node_index += 1
        

        #creating hold arcs
        for gh in self.nodes:
            node_dates = list(self.nodes[gh].keys())
            node_dates.sort()
            for i in range(len(node_dates) - 1):
                arc_orig_date = node_dates[i]
                arc_dest_date = node_dates[i+1]
                a = self.main.creating_vehicles_code.Arc()
                a.orig_node = self.nodes[gh][arc_orig_date]
                a.dest_node = self.nodes[gh][arc_dest_date]
                a.cost = 0
                if self.add_arc_to_dic(a):
                    raise
                else:
                    arc_index += 1
                    a.orig_node.output_arcs.append(a)
                    a.dest_node.input_arcs.append(a)
                
            
            
        
        
        print('added %s nodes and %s arcs' %(node_index, arc_index))
        
        
        
        
    def create_vehicles(self):
        best_cost, best_vehicles, best_itineraries, best_utilization = None, None, None, None
        order_types = ['slack_decreasing', 'slack_increasing', 'distance_decresing', 'distance_incresing']
        order_types += ['random' for i in range(self.main.optimization_iteration)]
        for order_type in order_types:
            print(order_type)
            cost, vehicles, itineraries, u = self.get_a_solution(order_type)
            print(cost)
            if best_cost == None:
                best_cost, best_vehicles, best_itineraries, best_utilization = cost, vehicles, itineraries, u
            elif cost < best_cost:
                best_cost, best_vehicles, best_itineraries, best_utilization = cost, vehicles, itineraries, u
        
        return best_cost, best_vehicles, best_itineraries, best_utilization
            
            
    def get_a_solution(self, order_type):
        current_cap = {}
        current_load = {}
        for orig_gh in self.arcs:
            for orig_date in self.arcs[orig_gh]:
                for dest_gh in self.arcs[orig_gh][orig_date]:
                    for dest_date in self.arcs[orig_gh][orig_date][dest_gh]:
                        current_cap[(orig_gh, orig_date, dest_gh, dest_date)] = 0
                        current_load[(orig_gh, orig_date, dest_gh, dest_date)] = 0
        
        if order_type == 'random':
            demand_ids = list(range(len(self.demand_list)))
            self.main.random.shuffle(demand_ids)
        elif order_type == 'slack_increasing':
            slacks = []
            for i in range(len(self.demand_list)):
                demand = self.demand_list[i]
                slack = (demand[3]-demand[1]).total_seconds()
                slacks.append((slack, i))
            slacks.sort()
            demand_ids = [item[1] for item in slacks]
        elif order_type == 'slack_decreasing':
            slacks = []
            for i in range(len(self.demand_list)):
                demand = self.demand_list[i]
                slack = (demand[3]-demand[1]).total_seconds()
                slacks.append((slack, i))
            slacks.sort(reverse = True)
            demand_ids = [item[1] for item in slacks]
        elif order_type == 'distance_incresing':
            distances = [] 
            for i in range(len(self.demand_list)):
                demand = self.demand_list[i]
                distance = self.main.get_travel_time(demand[0], demand[1])
                distances.append((distance, i))
            distances.sort()
            demand_ids = [item[1] for item in distances]
        elif order_type == 'distance_decresing':
            distances = [] 
            for i in range(len(self.demand_list)):
                demand = self.demand_list[i]
                distance = self.main.get_travel_time(demand[0], demand[1])
                distances.append((distance, i))
            distances.sort(reverse = True)
            demand_ids = [item[1] for item in distances]
           
        #slack increasing
        
        
        itineraries = {}
        for i in demand_ids:
            demand = self.demand_list[i]
            path = self.get_shortest_path(current_cap, current_load, demand)
            itineraries[i] = path
            for arc_key in path:
                current_load[arc_key] = current_load[arc_key] + demand[-1]
                c, cap = self.main.get_minimum_cost_vehicle(arc_key[0], arc_key[2], current_load[arc_key])
                current_cap[arc_key] = cap
        solution_cost = 0 
        vehicles = {} #key: arc_key, value: cap
        utilizations = [] 
        for arc_key in current_load:
            if current_load[arc_key] > 0:
                c, cap = self.main.get_minimum_cost_vehicle(arc_key[0], arc_key[2], current_load[arc_key])
                vehicles[arc_key] = cap
                solution_cost += c
                utilizations.append(current_load[arc_key] / cap)
        return solution_cost, vehicles, itineraries, sum(utilizations)/len(utilizations)
        
    
    def get_shortest_path(self, current_cap, current_load, demand):
        demand_orig_gh, demand_orig_date, demand_dest_gh, demand_dest_date, weight = demand
        model = self.main.gp.Model()
        variables = {} 
        '''
        -for each arc, add the arc variable to dictionary
        -calculate the arc cost 
        -add it to obj
        '''
        obj = 0
        for arc_key in current_cap:
            x = model.addVar(lb = 0, ub = 1)
            variables[arc_key] = x
            if arc_key[0] == arc_key[2]:
                continue
            available_cap = current_cap[arc_key] - current_load[arc_key]
            if weight <= available_cap:
                cost = self.main.optimization_little_m
            else:
                current_cost, total_cap = self.main.get_minimum_cost_vehicle(arc_key[0], arc_key[2], current_load[arc_key])
                next_cost, total_cap = self.main.get_minimum_cost_vehicle(arc_key[0], arc_key[2], weight + current_load[arc_key])
                cost = next_cost - current_cost 
            obj += cost * x
        '''
        for each node add flow constraint
        '''
        for gh in self.nodes:
            for d in self.nodes[gh]:
                n = self.nodes[gh][d]
                flow = 0 
                for a in n.input_arcs:
                    flow += variables[(a.orig_node.hub, a.orig_node.date, a.dest_node.hub, a.dest_node.date)]
                for a in n.output_arcs:
                    flow -= variables[(a.orig_node.hub, a.orig_node.date, a.dest_node.hub, a.dest_node.date)]
                if gh == demand_orig_gh and d == demand_orig_date:
                    rhs = -1
                elif gh == demand_dest_gh and d == demand_dest_date:
                    rhs = 1
                else:
                    rhs = 0
                model.addConstr(flow == rhs)
                
        model.setObjective(obj, self.main.gp.GRB.MINIMIZE)
        model.setParam('OutputFlag', 0)
        model.optimize()
        if model.Status != 2:
            raise
        path = [] 
        for arc_key in variables:
            if variables[arc_key].x == 1:
                if arc_key[0] != arc_key[2]:
                    path.append(arc_key)
        return path

                    
                    
                    
                    
        
            
        
        
        
        
                        





# def get_value(demands, ghs):
#     #1. create nodes 
#     demand_dates = []
#     for k in demands.keys():
#         demand_dates.append(demands[k][1])
#         demand_dates.append(demands[k][3])
#     min_demand_date, max_demand_date = min(demand_dates), max(demand_dates)
#     max_travel_time = 0
#     for orig_gh in ghs:
#         for dest_gh in ghs:
#             if orig_gh != dest_gh:
#                 travel_time = input_data.travel_times.get_travel_time(orig_gh, dest_gh)
#                 if max_travel_time < travel_time:
#                     max_travel_time = travel_time
#     nodes = {}
#     for node_date in range(min_demand_date, max_demand_date + max_travel_time + input_data.time_descretization, input_data.time_descretization):
#         for node_hub in ghs:
#             node = Node()
#             node.hub = node_hub
#             node.date = node_date
#             nodes[(node_hub, node_date)] = node
#     #2. create arcs
#     #create travel arcs
#     arcs = {}
#     for k in nodes.keys():
#         arc_orig_node = nodes[k]
#         arc_orig_gh = arc_orig_node.hub
#         arc_orig_date = arc_orig_node.date    
#         for arc_dest_gh in ghs:
#             if arc_dest_gh != arc_orig_gh:
#                 arc_travel_time = input_data.travel_times.get_travel_time(arc_orig_gh, arc_dest_gh)
#                 arc_dest_date = arc_orig_date + arc_travel_time 
#                 arc_dest_date = math.ceil(arc_dest_date / input_data.time_descretization) * input_data.time_descretization
#                 if arc_dest_date <= max_demand_date:
#                     arc = Arc()
#                     arc.cost = arc_travel_time
#                     arc.orig_node = nodes[(arc_orig_gh, arc_orig_date)]
#                     arc.dest_node = nodes[(arc_orig_gh, arc_orig_date)]
#                     arcs[(arc_orig_gh, arc_orig_date, arc_dest_gh, arc_dest_date)] = arc
#     #create hold arcs
#     for gh in ghs:
#         for arc_orig_date in range(min_demand_date, max_demand_date, input_data.time_descretization):
#             arc_dest_date = arc_orig_date + input_data.time_descretization
#             arc = Arc()
#             arc.cost = 0
#             arc.orig_node = nodes[(gh, arc_orig_date)]
#             arc.dest_node = nodes[(gh, arc_dest_date)]
#             arcs[(gh, arc_orig_date, gh, arc_dest_date)] = arc
#     #3. creating model variables and putting them on arcs and nodes
#     '''
#     go through arcs
#         for each demand id create a variable
#         put the variable in arc
#         put the variable in the orig and dest nodes
#         put the binary variable
#     '''
#     model = gp.Model()
#     for arc_key in arcs.keys():
#         orig_node = nodes[(arc_key[0], arc_key[1])]
#         dest_node = nodes[(arc_key[2], arc_key[3])]
#         arc = arcs[arc_key]
#         for demand_id in demands.keys():
#             x = model.addVar(lb = 0)
#             arc.flow_variables[demand_id] = x
#             if demand_id not in orig_node.output_arcs.keys():
#                 orig_node.output_arcs[demand_id] = [] 
#             if demand_id not in dest_node.input_arcs.keys():
#                 dest_node.input_arcs[demand_id] = []
#             orig_node.output_arcs[demand_id].append(x)
#             dest_node.input_arcs[demand_id].append(x)
#         y = model.addVar(lb = 0, ub = 1, vtype = GRB.BINARY)
#         arc.binary_variable = y
          
 
#     '''
    
#     #4. create model constraints
    
    
#     for each demand id 
#         for each node
#             flow constraint
#     for each arc
#         binary constraint
#     '''
    
    
#     for demand_id in demands.keys():
#         demand_orig_node_key = (demands[demand_id][0], demands[demand_id][1])
#         demand_dest_node_key = (demands[demand_id][2], demands[demand_id][3])
#         for node_key in nodes.keys():
#             if node_key == demand_orig_node_key:
#                 flow_constraint_rhs = 1
#             elif node_key == demand_dest_node_key:
#                 flow_constraint_rhs = -1
#             else:
#                 flow_constraint_rhs = 0
#             node = nodes[node_key]
#             flow_constraint_lhs = 0
#             arc_exists = False
#             if demand_id in node.output_arcs.keys():
#                 for arc_var in node.output_arcs[demand_id]:
#                     flow_constraint_lhs += arc_var
#                     arc_exists = True
#             if demand_id in node.input_arcs.keys():
#                 for arc_var in node.input_arcs[demand_id]:
#                     flow_constraint_lhs += -1 * arc_var
#                     arc_exists = True
#             if arc_exists:
#                 model.addConstr(flow_constraint_lhs == flow_constraint_rhs)
    
    
    
#     for arc_key in arcs.keys():
#         arc = arcs[arc_key]
#         lhs = 0
#         rhs = 0
#         if bool(arc.flow_variables):
#             for demand_id in arc.flow_variables.keys():
#                 lhs += arc.flow_variables[demand_id]
#                 rhs += arc.binary_variable 
#             model.addConstr(lhs <= rhs)
    
   
#     #5. add objective 
#     obj = 0
#     for arc_key in arcs.keys():
#         arc = arcs[arc_key]
#         obj += arc.cost * arc.binary_variable
#     model.setObjective(obj, GRB.MINIMIZE)

    
#     #6. get solution
#     model.setParam('OutputFlag', 0)
#     model.optimize()
   
    
#     return model.objVal

    


# def record_costs(demand_file_directories, ghs):
#     output_list = [] 
#     for demand_file_directory in demand_file_directories:
#         df = pd.read_csv(demand_file_directory)
#         demands = {}
#         for index, row in df.iterrows():
#             demands[index] = tuple(list(row)[:-1])
#         start_time = time.time()
#         value = get_value(demands, ghs)
#         print("+++++++++++++++++++++++++++++++")
#         print("optimal value %s" % (value))
#         print("value calculation--- %s seconds ---" % (time.time() - start_time))
#         print("+++++++++++++++++++++++++++++++")
#         state_id = int(demand_file_directory.replace("_demand.csv","").replace("../output/state_",""))
#         output_list.append((state_id, value)) 
        
#     output_list.sort()
#     df = pd.DataFrame(output_list, columns = ['state_id', 'value'])
#     df.to_csv("../output/values.csv", index = False)




# record_costs(file_directories, input_data.travel_times.get_all_hubs())


if __name__ == '__main__':
    print('main imported in value calculator')
    import main_code







