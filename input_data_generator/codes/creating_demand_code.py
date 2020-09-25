# -*- coding: utf-8 -*-

class CreateDemand():
    def __init__(self, main):
        self.main = main
        self.created_demand = [] 
        self.create_demand()
        
    
    def get_demand_eligibility(self, orig_date, orig_gh, dest_date, dest_gh):
        if orig_gh == dest_gh:
            return False
        slack = (dest_date - orig_date).total_seconds() * 1000.0
        tt = self.main.get_travel_time(orig_gh, dest_gh)
        if slack < tt:
            return False
        if slack > self.main.maximum_demand_slack:
            return False
        return True
        
    def generate_node(self):
        s = self.main.random.randint(0, int((self.main.demand_end_date - self.main.demand_start_date).total_seconds()))
        s =  self.main.time_descretization * round(1000.0 * s / self.main.time_descretization) / 1000.0
        d = self.main.demand_start_date + self.main.datetime.timedelta(seconds = s)
        gh = self.main.random.choice(self.main.ghs)
        return d, gh
        
    def create_demand(self):
        for i in range(self.main.number_of_demands):
            mean_demand = 0
            while mean_demand <= 0:
                mean_demand = round(self.main.np.random.normal(self.main.mean_of_demand_mean, self.main.std_of_demand_mean),1)
            proceed = True
            while proceed:
                orig_date, orig_gh = self.generate_node()
                dest_date, dest_gh = self.generate_node()
                if self.get_demand_eligibility(orig_date, orig_gh, dest_date, dest_gh):
                    proceed = False
                    weight = 0
                    while weight <= 0:
                        weight = round(self.main.np.random.normal(self.main.mean_of_demand_mean, self.main.std_of_demand_mean),2)
                    self.created_demand.append((orig_gh, orig_date, dest_gh, dest_date, weight))

        




if __name__ == '__main__':
    print('main called from creating demand')
    import main_code










