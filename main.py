import simpy, numpy, random
import settings as setts
from statistic import Statistic

class TrucksColumn:

    GLOBAL_COLUMN_COUNT = 0

    def __init__(self, env: simpy.Environment, statistic: Statistic):
        self.env = env
        self.statistic = statistic
        self.id = TrucksColumn.GLOBAL_COLUMN_COUNT
        TrucksColumn.GLOBAL_COLUMN_COUNT += 1
        self.unloaded_count = 0
        self.generate_trucks()

    def generate_trucks(self):
        self.trucks = []
        types_quantity = int( 
            numpy.random.triangular(
                left=setts.COLUMN_MIN_TRUCKS, 
                right=setts.COLUMN_MAX_TRUCKS, 
                mode=setts.COLUMN_MODE_TRUCKS
            )
        )
        for i in range(types_quantity):
            trucks_type = numpy.random.choice( [i for i in range(setts.COLUMN_TRUCKS_TYPES_COUNT)] )
            truck_types_count = int(
                numpy.random.normal(
                    loc=setts.COLUMN_TRUCKS_TYPES_SAME_PARAMS_MATHEXP,
                    scale=setts.COLUMN_TRUCKS_TYPES_SAME_PARAMS_STDEVIATION
                )
            )
            self.trucks += [trucks_type for i in range(truck_types_count)]
        random.shuffle(self.trucks)        

    def unloaded_truck(self):
        self.unloaded_count += 1
        if self.unloaded_count == len(self.trucks):
            print(f'Колонна №{self.id} разгружена ')
            self.statistic.base_work_times.append(-1 * self.env.now)
    

class Base:
    def __init__(self, env: simpy.Environment, statistic: Statistic):
        self.env = env
        self.statistic = statistic
        self.unloading_points = simpy.Resource(env, capacity=setts.BASE_UNLOADING_POINTS_COUNT)
        self.cranes = simpy.Resource(env, capacity=setts.BASE_CRANES_COUNT)
        self.forklifts = simpy.Resource(env, capacity=setts.BASE_FORKLIFTS_COUNT)
            
    def wait_unloading_point(self, column: TrucksColumn, statistic: Statistic):
        for truck in column.trucks:
            unloading = self.unloading_points.request()
            yield unloading
            self.env.process(self.unload_truck(truck, column, unloading))

    def unload_truck(self, truck, column, unloading):
        forklift = crane = None
        unload_time_start = self.env.now
        if truck in setts.COLUMN_TRUCKS_TYPES_REQUIRES_CRANE:
            crane = self.cranes.request()
            yield crane
        if truck in setts.COLUMN_TRUCKS_TYPES_REQUIRES_FORKLIFT:
            forklift = self.forklifts.request()
            yield forklift

        time_exponenta = setts.COLUMN_TRUCKS_TYPES_UNLOADING_PARAMS[truck]
        unloading_time = numpy.random.exponential(time_exponenta)
        yield self.env.timeout(unloading_time)
        
        column.unloaded_truck()
        statistic.unload_times.append(self.env.now - unload_time_start)
        self.unloading_points.release(unloading)
        if truck in setts.COLUMN_TRUCKS_TYPES_REQUIRES_CRANE:
            statistic.machines_work_time += self.env.now - unload_time_start 
            self.cranes.release(crane)
        if truck in setts.COLUMN_TRUCKS_TYPES_REQUIRES_FORKLIFT:
            statistic.machines_work_time += self.env.now - unload_time_start
            self.forklifts.release(forklift)
        
    
def model_base(env: simpy.Environment, statistic: Statistic):
    base = Base(env, statistic)
    while True:
        column = TrucksColumn(env, statistic)
        print(f'Колонна №{column.id} прибыла ')
        statistic.base_work_times.append(env.now)
        env.process(base.wait_unloading_point(column, statistic))
        next_arrival_time = int( numpy.random.exponential(setts.COLUMN_ARRIVAL_TIME_DIFFERENS_PARAM) )
        yield env.timeout(next_arrival_time)
        
env = simpy.Environment()
statistic = Statistic()
env.process(model_base(env, statistic))
env.run(until=setts.BASE_MODELLING_TIME)
statistic.print_mean_statistic()
