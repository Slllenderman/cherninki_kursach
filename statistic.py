import statistics
import settings as setts
import matplotlib.pyplot as plt

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

    def get_overlapping_sum(self):
        last_break_time = 0
        overlap_sum = 0
        overlap_levels = 0
        last_closed = 0
        for stat in self.time_list:
            if stat.time >= 0:
                overlap_levels += 1
            else:
                overlap_levels -= 1
                last_closed = stat.time
            if last_break_time == -1:
                last_break_time = stat.time
            if overlap_levels == 0:
                overlap_sum += abs(stat.time) - last_break_time
                last_break_time = -1
        if overlap_levels != 0:
            overlap_sum += abs(last_closed) - last_break_time
            overlap_sum += setts.MODELLING_TIME - abs(last_closed)
        return overlap_sum


class Statistic:
    def __init__(self, env):
        self.env = env
        self.column_live_times = TimeObjStatistic(env)
        self.truck_unloads_times = TimeObjStatistic(env)
        self.crane_load_times = TimeObjStatistic(env)
        self.forklift_load_times = TimeObjStatistic(env)
        self.unload_point_wait_times = TimeObjStatistic(env)
        
        self.unloading_queue_times = []

        self.mean_unload_times = []
        self.mean_crane_workloads = []
        if setts.DRAW_DYNAMIC_GRAPH:
            plt.ion()
            self.mean_unload_time_plot = plt.plot([], [], label='Среднее время разгрузки')[0]
            self.mean_crane_workloads_plot = plt.plot([], [], label='Средне время разгрузки с использованием крана')[0]
            plt.legend()
            plt.pause(0.1)
        
    # Хранить tuple's формата время, длина очереди
    def set_unloading_queue(self, queue_len):
        self.unloading_queue_times.append((self.env.now, queue_len))

    def set_column_arrived(self, column):
        if setts.DRAW_TEXT_STAT:
            print(f'Колонна №{column.id} прибыла')
            self.column_live_times.set_time(column)

    def set_column_departs(self, column):
        if setts.DRAW_TEXT_STAT:
            print(f'Колонна №{column.id} разгружена')
            self.column_live_times.set_time(column, -1)
            self.column_live_times.append_dtime(column)
    
    def set_forklift_unload_start(self, forklift):
        if setts.DRAW_TEXT_STAT:
            self.forklift_load_times.set_time(forklift)

    def set_forklift_unload_finish(self, forklift):
        if setts.DRAW_TEXT_STAT:
            self.forklift_load_times.set_time(forklift, -1)
            self.forklift_load_times.append_dtime(forklift)

    def set_truck_unload_start(self, truck):
        if setts.DRAW_TEXT_STAT or setts.DRAW_DYNAMIC_GRAPH:
            self.truck_unloads_times.set_time(truck)       

    def set_truck_unload_finish(self, truck):
        if setts.DRAW_TEXT_STAT or setts.DRAW_DYNAMIC_GRAPH:
            self.truck_unloads_times.set_time(truck, -1)
            self.truck_unloads_times.append_dtime(truck)
            if setts.DRAW_DYNAMIC_GRAPH:
                mean_unload_time = statistics.mean(self.truck_unloads_times.dtimes)
                self.mean_unload_times.append((self.env.now, mean_unload_time))
                self.mean_unload_time_plot = self.plot_step(
                    self.mean_unload_time_plot, 
                    self.mean_unload_times, 
                    color='orange', 
                    label='Среднее время разгрузки'
                )
        
    def set_crane_work_start(self, crane):
        if setts.DRAW_TEXT_STAT or setts.DRAW_DYNAMIC_GRAPH:
            self.crane_load_times.set_time(crane)

    def plot_step(self, plot, series, color='g', label='a'):
        if len(series) % setts.PLOT_RATE == 0:
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
        if setts.DRAW_TEXT_STAT or setts.DRAW_DYNAMIC_GRAPH:
            self.crane_load_times.set_time(crane, -1)
            self.crane_load_times.append_dtime(crane)
            if setts.DRAW_DYNAMIC_GRAPH:
                mean_crane_workload = statistics.mean(self.crane_load_times.dtimes)
                self.mean_crane_workloads.append((self.env.now, mean_crane_workload))
                self.mean_crane_workloads_plot = self.plot_step(
                    self.mean_crane_workloads_plot,
                    self.mean_crane_workloads, 
                    color='blue', 
                    label='Средне время разгрузки с использованием крана'
                )
    
    def print_mean_statistic(self):
        if setts.DRAW_TEXT_STAT:
            mean_unload_time = statistics.mean(self.truck_unloads_times.dtimes)
            mean_column_livetime = statistics.mean(self.column_live_times.dtimes)
            mean_crane_workload = statistics.mean(self.crane_load_times.dtimes)
            mean_forklift_workload = statistics.mean(self.forklift_load_times.dtimes)
            print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print('Среднее время:')
            print(f'    - пребывания колонны на базе: {round(mean_column_livetime, 0)}')
            print(f'    - выгрузки грузовика: {round(mean_unload_time, 2)}')
            print(f'    - выгрузки с использованием кранов: {round(mean_crane_workload, 2)}')
            print(f'    - выгрузки с использованием погручзиков: {round(mean_forklift_workload, 2)}')
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

    def print_workload_statistic(self):
        if setts.DRAW_TEXT_STAT:
            base_work_time = self.column_live_times.get_overlapping_sum()
            technic_work_time = self.forklift_load_times.get_time_sum() + self.crane_load_times.get_time_sum()
            print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            print('Процентное соотношение:')
            print(f'    - работы всей базы: {round((base_work_time / setts.MODELLING_TIME) * 100, 2)}%')
            print(f'    - загруженности технинки: {round(technic_work_time /  (setts.MODELLING_TIME * (setts.BASE_CRANES_COUNT + setts.BASE_FORKLIFTS_COUNT)) * 100, 2)}%')
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')