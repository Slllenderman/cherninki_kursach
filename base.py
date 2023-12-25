import simpy
import settings as setts
from numpy.random import shuffle
from statistic import Statistic
from trucks import Truck, TrucksColumn

class UnloadingPoints:
    def __init__(self, env, statistic):
        self.env = env
        self.statistic = statistic
        self.points = simpy.Resource(env, capacity=setts.BASE_UNLOADING_POINTS_COUNT)
        self.points_busy = [False for _ in range(setts.BASE_UNLOADING_POINTS_COUNT)]
        self.choice_strategies = {
            'random' : self.random_choice_strategy,
            'sequintial' : self.sequential_choice_strategy
        }
        self.choice_strategy = self.choice_strategies[setts.BASE_UNLOADING_CHOICE_STRATEGY]

    def get_pointnum(self):
        for point_num in self.choice_strategy():
            if not self.points_busy[point_num]:
                self.points_busy[point_num] = True
                return point_num
    
    def release_point(self, point):
        self.points_busy[getattr(point, 'point_num')] = False
        self.points.release(point)

    def sequential_choice_strategy(self):
        return [i for i in range(setts.BASE_UNLOADING_POINTS_COUNT)]

    def random_choice_strategy(self):
        choices = [i for i in range(setts.BASE_UNLOADING_POINTS_COUNT)]
        shuffle(choices)
        return choices

class Base:
    def __init__(self, env: simpy.Environment, statistic: Statistic):
        self.env = env
        self.statistic = statistic
        self.unloading_points = UnloadingPoints(self.env, self.statistic)
        self.cranes = simpy.Resource(env, capacity=setts.BASE_CRANES_COUNT)
        self.forklifts = simpy.Resource(env, capacity=setts.BASE_FORKLIFTS_COUNT)

    def wait_unloading_point(self, column: TrucksColumn):
        for truck in column.trucks:
            unloading = self.unloading_points.points.request()
            self.statistic.set_unloading_queue(len(self.unloading_points.points.queue) + len(self.forklifts.queue) + len(self.cranes.queue))
            yield unloading
            point_num = self.unloading_points.get_pointnum()
            setattr(unloading, 'point_num', point_num)
            self.env.process(self.unload_truck(truck, unloading))

    def unload_truck(self, truck: Truck, unloading):
        self.statistic.set_truck_unload_start(truck)
        truck.request_technic(self.cranes, self.forklifts)
        if truck.needs_crane: 
            yield truck.crane
            self.statistic.set_crane_work_start(truck.crane)
        if truck.needs_forklift: 
            yield truck.forklift
            self.statistic.set_forklift_unload_start(truck.forklift)
        yield self.env.timeout(truck.unload_time)
        self.unloading_points.release_point(unloading)
        truck.release_technic(self.cranes, self.forklifts)
        self.statistic.set_truck_unload_finish(truck)
        self.statistic.set_unloading_queue(len(self.unloading_points.points.queue) + len(self.forklifts.queue) + len(self.cranes.queue))
            