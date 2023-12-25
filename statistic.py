import statistics
import settings as setts

class TimeObject:
    def __init__(self, id, obj, time):
        self.id = id
        self.obj = obj
        self.time = time

    
class TimeObjStatistic:
    def __init__(self, env):
        self.env = env
        self.time_list = []
        self.dtimes = []

    def set_time(self, obj, prefix = 1):
        self.time_list.append(
            TimeObject(
                id = obj.__hash__(),
                obj = obj,
                time = prefix * self.env.now
            ) 
        )

    def append_dtime(self, obj):
        dtime = self.get_dtime(obj)
        self.dtimes.append(dtime)

    def get_dtime(self, obj):
        times = [stat for stat in self.time_list if stat.id == obj.__hash__()]
        prev_time, next_time = times
        if prev_time.time < 0 or next_time.time > 0:
            raise ValueError("DTime statistic error")
        return abs(next_time.time + prev_time.time)

class Statistic:
    def __init__(self, env):
        self.env = env
        self.column_live_times = TimeObjStatistic(env)
        self.truck_unloads_times = TimeObjStatistic(env)
        self.crane_load_times = TimeObjStatistic(env)
        self.forklift_load_times = TimeObjStatistic(env)
        self.unload_point_wait_times = TimeObjStatistic(env)
        
    def set_column_arrived(self, column):
        print(f'Колонна №{column.id} прибыла')
        self.column_live_times.set_time(column)

    def set_column_departs(self, column):
        print(f'Колонна №{column.id} разгружена')
        self.column_live_times.set_time(column, -1)
        self.column_live_times.append_dtime(column)
    
    def set_truck_unload_start(self, truck):
        self.truck_unloads_times.set_time(truck)

    def set_truck_unload_finish(self, truck):
        self.truck_unloads_times.set_time(truck, -1)
        self.truck_unloads_times.append_dtime(truck)
    
    def set_crane_work_start(self, crane):
        self.crane_load_times.set_time(crane)

    def set_crane_unload_finish(self, crane):
        self.crane_load_times.set_time(crane, -1)
        self.crane_load_times.append_dtime(crane)
    
    def set_forklift_unload_start(self, forklift):
        self.forklift_load_times.set_time(forklift)

    def set_forklift_unload_finish(self, forklift):
        self.forklift_load_times.set_time(forklift, -1)
        self.forklift_load_times.append_dtime(forklift)
    
    def print_mean_statistic(self):
        mean_unload_time = statistics.mean(self.truck_unloads_times.dtimes)
        mean_column_livetime = statistics.mean(self.column_live_times.dtimes)
        mean_crane_workload = statistics.mean(self.crane_load_times.dtimes)
        mean_forklift_workload = statistics.mean(self.forklift_load_times.dtimes)
        print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
        print(f'Среднее время пребывания колонны на базе: {round(mean_column_livetime, 0)}')
        print(f'Среднее время выгрузки грузовика: {round(mean_unload_time, 2)}')
        print(f'Среднее время использование кранов: {round(mean_crane_workload, 2)}')
        print(f'Среднее время использование погручзиков: {round(mean_forklift_workload, 2)}')
        print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')