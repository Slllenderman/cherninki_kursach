import statistics
import matplotlib.pyplot as plt

BASE_FORKLIFTS_COUNT = 10
BASE_CRANES_COUNT = 10
BASE_MODELLING_TIME = 43200

DRAW_EXPERIMENT = False
DRAW_TEXT_STAT = True if not DRAW_EXPERIMENT else False
DRAW_DYNAMIC_GRAPH = False if not DRAW_EXPERIMENT else False
PLOT_RATE = 100

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

    def get_time_sum(self):
        sum = 0
        for times in self.dtimes:
            sum += times
        return sum


class Statistic:
    def __init__(self, env):
        self.env = env
        self.column_live_times = TimeObjStatistic(env)
        self.truck_unloads_times = []
        self.crane_load_times = TimeObjStatistic(env)
        self.forklift_load_times = TimeObjStatistic(env)
        self.unload_point_wait_times = TimeObjStatistic(env)
        self.technic_queue_time = []
        self.unloading_queue_times = []

        self.mean_unload_times = []
        self.mean_crane_workloads = []
        if DRAW_DYNAMIC_GRAPH:
            plt.ion()
            self.mean_unload_time_plot = plt.plot([], [], label='Среднее время разгрузки')[0]
            self.mean_crane_workloads_plot = plt.plot([], [], label='Средне время разгрузки с использованием крана')[0]
            plt.legend()
            plt.pause(0.1)
        
    # Хранить tuple's формата время, длина очереди
    def set_unloading_queue(self, queue_len):
        self.unloading_queue_times.append((self.env.now, queue_len))

    def set_technic_queue(self, queue_len):
        self.technic_queue_time.append((self.env.now, queue_len))

    def set_column_arrived(self, column):
        if DRAW_TEXT_STAT:
            print(f'Колонна №{column.id} прибыла')
            self.column_live_times.set_time(column)

    def set_column_departs(self, column):
        if DRAW_TEXT_STAT:
            print(f'Колонна №{column.id} разгружена')
            self.column_live_times.set_time(column, -1)
            self.column_live_times.append_dtime(column)
    
    def set_forklift_unload_start(self, forklift):
        if DRAW_TEXT_STAT:
            self.forklift_load_times.set_time(forklift)

    def set_forklift_unload_finish(self, forklift):
        if DRAW_TEXT_STAT:
            self.forklift_load_times.set_time(forklift, -1)
            self.forklift_load_times.append_dtime(forklift)

    def set_truck_unload_start(self, truck):
        if DRAW_TEXT_STAT:
            self.truck_unloads_times.set_time(truck)       

    def set_truck_unload_finish(self, truck):
        if DRAW_TEXT_STAT:
            self.truck_unloads_times.set_time(truck, -1)
            self.truck_unloads_times.append_dtime(truck)
        
    def set_crane_work_start(self, crane):
        if DRAW_TEXT_STAT:
            self.crane_load_times.set_time(crane)

    def plot_step(self, plot, series, color='g', label='a'):
        if len(series) % PLOT_RATE == 0:
            plot.remove()
            plot = plt.plot(
                [x[0] for x in series], 
                [x[1] for x in series], 
                color=color,
                label=label
            )[0]
            plt.legend()
            plt.pause(1e-5)
        return plot

    def set_crane_unload_finish(self, crane):
        if DRAW_TEXT_STAT:
            self.crane_load_times.set_time(crane, -1)
            self.crane_load_times.append_dtime(crane)
    
    def print_mean_statistic(self):
        if DRAW_TEXT_STAT:
            mean_unload_time = statistics.mean(self.truck_unloads_times)
            mean_crane_workload = statistics.mean(self.crane_load_times.dtimes)
            mean_forklift_workload = statistics.mean(self.forklift_load_times.dtimes)
            technic_work_time = self.forklift_load_times.get_time_sum() + self.crane_load_times.get_time_sum()

            technic_queue = 0
            for value in self.technic_queue_time:
                technic_queue += value[1]
            technic_queue /= len(self.technic_queue_time) if len(self.technic_queue_time) != 0 else 1

            print(f'Среднее время выгрузки грузовика: {round(mean_unload_time, 2)}')
            print(f'Среднее время использованием кранов: {round(mean_crane_workload, 2)}')
            print(f'Среднее время использованием погручзиков: {round(mean_forklift_workload, 2)}')
            print(f'Cреднее число машин в ожидании техники: {round(technic_queue, 2)}')
            print(f'Процент загруженности технинки: {round(technic_work_time /  (BASE_MODELLING_TIME * (BASE_CRANES_COUNT + BASE_FORKLIFTS_COUNT)) * 100, 2)}%')