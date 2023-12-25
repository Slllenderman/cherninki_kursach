import simpy
import settings as setts
from numpy import random
from statistic import Statistic


class Truck:
    def __init__(self, type_param: int, unload_event, statistic: Statistic):
        self.unload_time = random.exponential(type_param)
        self.unload_event = unload_event
        self.needs_crane = random.random() < setts.TRUCK_REQUIRES_FORKLIFT_PROBABILITY
        self.needs_forklift = random.random() < setts.TRUCK_REQUIRES_CRANE_PROBABILITY
        self.forklift = None
        self.crane = None
        self.statistic = statistic
    
    def request_technic(self, cranes: simpy.Resource, forklifts: simpy.Resource):
        if self.needs_crane:
            self.crane = cranes.request()
        if self.needs_forklift:
            self.forklift = forklifts.request() 

    def release_technic(self, cranes: simpy.Resource, forklifts: simpy.Resource):
        if self.needs_crane: 
            cranes.release(self.crane)
            self.statistic.set_crane_unload_finish(self.crane)
        if self.needs_forklift:
            forklifts.release(self.forklift)
            self.statistic.set_forklift_unload_finish(self.forklift)
        self.unload_event()



class TrucksColumn:

    GLOBAL_COLUMN_COUNT = 0

    def __init__(self, env: simpy.Environment, statistic: Statistic):
        self.env = env
        self.statistic = statistic
        self.id = TrucksColumn.GLOBAL_COLUMN_COUNT
        TrucksColumn.GLOBAL_COLUMN_COUNT += 1
        self.unloaded_count = 0
        self.generate_trucks()
        self.statistic.set_column_arrived(self)

    def unloaded_truck_event(self):
        self.unloaded_count += 1
        if self.unloaded_count == len(self.trucks):
            self.statistic.set_column_departs(self)

    def generate_trucks(self):
        self.trucks = []
        types_quantity = int( 
            random.triangular(
                left=setts.COLUMN_MIN_TRUCKS, 
                right=setts.COLUMN_MAX_TRUCKS, 
                mode=setts.COLUMN_MODE_TRUCKS
            )
        )
        for _ in range(types_quantity):
            truck_type = random.choice( setts.TRUCK_TYPES_MATHEXPS )
            truck_types_count = int(
                random.normal(
                    loc=setts.COLUMN_TRUCKS_TYPES_SAME_PARAMS_MATHEXP,
                    scale=setts.COLUMN_TRUCKS_TYPES_SAME_PARAMS_STDEVIATION
                )
            )
            self.trucks += [Truck(truck_type, self.unloaded_truck_event, self.statistic) for _ in range(truck_types_count)]
        random.shuffle(self.trucks)