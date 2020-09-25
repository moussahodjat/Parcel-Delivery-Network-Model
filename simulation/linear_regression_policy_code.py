#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 11 19:10:53 2020

@author: Moussa
"""

#%%

class Policy:
    def __init__(self, main_object):
        self.main = main_object
        self.betas = None
        
        





    def get_action(self, d, v, current_period):
        #optimization
        n_locations = d.shape[0]
        n_dates = d.shape[1]
        current_period_array = d[:,int(current_period),:,:]
        current_period_non_zero = self.main.np.argwhere(current_period_array > 0)
        
        if len(current_period_non_zero) == 0:
            return {}, {}, 0, self.main.np.array(d)
        
        
        jk_i = {} #key: {(j,k) : [i]}
        ik_j = {} #{(i,k): [j]}
        ij_k = {} #(i,j): [k]}
        x_ijk = {} #key: (i,j,k)
        y_ij = {} #key: (i,j)
        # d_pd_jk = {} #key: (j,k)
        d_pd_discrete_jk = {} #key: (j,k)
        model = self.main.gp.Model()
        for item in current_period_non_zero:
            i = (int(item[0]), int(current_period))
            k = (int(item[1]), int(item[2]))
            for next_hub in range(n_locations):
                tt = self.main.inputs.travel_times_matrix[(i[0], next_hub)]
                if tt == 0:
                     tt_discrete = 1.0
                else:
                    tt_discrete = self.main.math.ceil(tt / self.main.inputs.time_discretization_factor)
                dest_time = float(current_period) + tt_discrete
                if dest_time <= n_dates - 1:
                    j = (int(next_hub), int(dest_time))
                    if (j,k) not in jk_i:
                        jk_i[(j,k)] = []
                    jk_i[(j,k)].append(i)
                    if (i,k) not in ik_j:
                        ik_j[(i,k)] = [] 
                    ik_j[(i,k)].append(j)
                    if (i,j) not in ij_k:
                        ij_k[(i,j)] = []
                    ij_k[(i,j)].append(k)
                    #variables
                    x_ijk[(i,j,k)] = model.addVar(lb = 0, ub = 1, vtype = self.main.gp.GRB.INTEGER, name = "x" + str(i) + "_" + str(j) + "_" + str(k)) 
                    if (i,j) not in y_ij:
                        y_ij[(i,j)] = model.addVar(lb = 0, ub = 1, vtype = self.main.gp.GRB.INTEGER, name = "y" + str(i[0]) + "_" + str(j[0])) 
                    # if (j,k) not in d_pd_jk:
                    #     d_pd_jk[(j,k)] = model.addVar(lb = 0, name = "d_pd"+str(j) + "_" + str(k))
                    if (j,k) not in d_pd_discrete_jk:
                        d_pd_discrete_jk[(j,k)] = model.addVar(lb = 0, ub = 1, vtype = self.main.gp.GRB.INTEGER, name = "d_pd_discrete"+str(j) + "_" + str(k))


        for key in ik_j:
            i = key[0]
            k = key[1]
            lhs = 0
            for j in ik_j[key]:
                lhs += x_ijk[(i,j,k)] 
            model.addConstr(lhs == 1)
        
        
        avail_cap = {}
        v_current_period_array = v[:, int(current_period), :, :]
        v_current_period_non_zero = self.main.np.argwhere(v_current_period_array > 0)
        for item in v_current_period_non_zero:
            avail_cap[(item[0], item[1])] = v_current_period_array[tuple(item)]
        
        M = self.main.np.sum(d)
        for key in ij_k:
            i,j = key
            rhs = 0
            for k in ij_k[key]:
                rhs += d[(i[0], i[1], k[0], k[1])]  * x_ijk[(i,j,k)]
            l1,l2 = i[0], j[0]
            if (l1, l2) in avail_cap:
                rhs -= avail_cap[(l1,l2)]
            lhs = M * y_ij[(i,j)] 
            model.addConstr(lhs >= rhs)
            
        
        for key in d_pd_discrete_jk:
            j,k = key
            rhs = d[(j[0], j[1], k[0], k[1])]
            for i in jk_i[(j,k)]:
                rhs += d[(i[0], i[1], k[0], k[1])] * x_ijk[(i,j,k)]
            model.addConstr(d_pd_discrete_jk[key] * M >= rhs)  
            # lhs = d_pd_jk[(j,k)]
            # model.addConstr(lhs == rhs)
            # model.addConstr(d_pd_discrete_jk[key] * M >= d_pd_jk[key])    
 
            
        obj = 0
        for key in y_ij:
            l1 = key[0][0]
            l2 = key[1][0]
            c = self.main.inputs.lowest_cost_vehicle_costs_matrix[(l1, l2)]
            obj += c * y_ij[key]
        
        for key in d_pd_discrete_jk:
            j,k = key
            obj += self.betas[(j[0], j[1], k[0], k[1])] * d_pd_discrete_jk[key]
            
        
        
            
        model.setObjective(obj, self.main.gp.GRB.MINIMIZE)
        model.setParam('OutputFlag', 0)
        model.optimize()
        
        
        
        
        if model.status != self.main.gp.GRB.Status.OPTIMAL:
            model.computeIIS()
            model.write("file.ilp")
            print(model.status, current_period)
            raise

        #get return values
        assignments = {}
        flows = {}  #includes the vehicles that might already be in the system
        d_pd = self.main.np.array(d)
        
        
        # print(model.status)
        for l1l2 in avail_cap:
            flows[l1l2] = 0
        
        for ij in y_ij:
            if y_ij[ij].x == 1.0:
                i,j = ij
                if i[0] != j[0]:
                    flows[(i[0],j[0])] = 0
        
        
        for ijk in x_ijk:
            if x_ijk[ijk].x == 1:
                i,j,k = ijk
                if ijk[0][0] != ijk[1][0]:
                    # print(i,j,k)
                    flows[(i[0],j[0])] += d[(i[0], i[1], k[0], k[1])]
                    assignments[(i[0], i[1], k[0], k[1])] = j[0]
                d_pd[(i[0], i[1], k[0], k[1])] = 0.0
                d_pd[(j[0], j[1], k[0], k[1])] = d_pd[(j[0], j[1], k[0], k[1])] + d[(i[0], i[1], k[0], k[1])]
        
        
        
        
        
        current_period_pd = d_pd[:, int(current_period), :, :]
        current_period_pd_non_zero = self.main.np.argwhere(current_period_pd > 0)
        if len(current_period_pd_non_zero != 0):
            raise
         
        cost_of_action = 0
        vehicles = {}
        for key in flows:
            load = flows[key]
            current_cap = 0
            if key in avail_cap:
                current_cap += avail_cap[key]
            if load > current_cap:
                l1, l2 = key
                orig_gh = self.main.inputs.index_to_location[l1]
                dest_gh = self.main.inputs.index_to_location[l2]
                needed_cap = load - current_cap
                cost, total_cap = self.main.inputs.get_minimum_cost_vehicle(orig_gh, dest_gh, needed_cap)
                vehicles[key] = total_cap 
                cost_of_action += cost
                
        # d_pd[d_pd > 0] = 1
                    
        return vehicles, assignments, cost_of_action, d_pd
      
        
           
        
        
        
        
        
     
        
        
        
        
        
        
if __name__ == '__main__':
    import main 
    main.run()
    # main.one_iteration()
    # main.initialize_inputs()
    # main.run_simulation()
    
#%%