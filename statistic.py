import statistics
import settings as setts
# Класс для сбора и вывода необходимой статистики грузовиков
class Statistic:
    def __init__(self):
        self.unload_times = []
        self.machines_work_time = 0
        self.base_work_times = []

    def print_mean_statistic(self):
        mean_unload_time = statistics.mean(self.unload_times)
        mean_machinex_load = self.machines_work_time / (setts.BASE_MODELLING_TIME * (setts.BASE_CRANES_COUNT + setts.BASE_FORKLIFTS_COUNT))
        
        columns_on_base = 0
        time_after_break = 0
        base_load = 0
        for time in self.base_work_times:
            if time_after_break == -1:
                time_after_break = time
            if time >= 0:
                columns_on_base += 1
            else:
                columns_on_base -= 1
            if columns_on_base == 0:
                base_load += abs(time) - time_after_break
                time_after_break = -1        
        
        print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')
        print(f'Среднее время выгрузки грузовика: {mean_unload_time}')
        print(f'Среднее значение загрузки техники: {round(mean_machinex_load * 100, 2)} %')
        print(f'Среднее значение работы всей базы: {round(base_load / setts.BASE_MODELLING_TIME * 100, 2)} %')
        print('\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n')