import simpy, numpy, random
from statistic import Statistic
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

COLUMN_MIN_TRUCKS = 4
COLUMN_MAX_TRUCKS = 10
COLUMN_MODE_TRUCKS = 8
COLUMN_TRUCKS_TYPES_COUNT = 10
COLUMN_TRUCKS_TYPES_SAME_PARAMS_MATHEXP = 14
COLUMN_TRUCKS_TYPES_SAME_PARAMS_STDEVIATION = 3 
COLUMN_TRUCKS_TYPES_UNLOADING_PARAMS = [22, 21, 27, 24, 17, 19, 22, 31, 28, 29]
COLUMN_COLUMN_BASE_ARRIVAL_TIME_DIFFERENS_PARAM = 540
COLUMN_TRUCKS_TYPES_REQUIRES_FORKLIFT = [0, 1, 2, 3]
COLUMN_TRUCKS_TYPES_REQUIRES_CRANE = [7, 8, 9]
BASE_FORKLIFTS_COUNT = 7
BASE_CRANES_COUNT = 5
BASE_UNLOADING_POINTS_COUNT = 10
BASE_MODELLING_TIME = 43200
ALPHA = 0.05

class Column:

    GLOBAL_COLUMN_COUNT = 0

    def __init__(self, env: simpy.Environment, statistic: Statistic):
        self.env = env
        self.statistic = statistic
        self.id = Column.GLOBAL_COLUMN_COUNT
        Column.GLOBAL_COLUMN_COUNT += 1
        self.unloaded_count = 0
        self.generate_trucks()

    def generate_trucks(self):
        self.trucks = []
        types_quantity = int( 
            numpy.random.triangular(
                left=COLUMN_MIN_TRUCKS, 
                right=COLUMN_MAX_TRUCKS, 
                mode=COLUMN_MODE_TRUCKS
            )
        )
        for i in range(types_quantity):
            trucks_type = numpy.random.choice( [i for i in range(COLUMN_TRUCKS_TYPES_COUNT)] )
            truck_types_count = int(
                numpy.random.normal(
                    loc=COLUMN_TRUCKS_TYPES_SAME_PARAMS_MATHEXP,
                    scale=COLUMN_TRUCKS_TYPES_SAME_PARAMS_STDEVIATION
                )
            )
            self.trucks += [trucks_type for i in range(truck_types_count)]
        random.shuffle(self.trucks)        

    def unloaded_truck(self):
        self.unloaded_count += 1
        if self.unloaded_count == len(self.trucks):
            print(f'Колонна №{self.id} разгружена ')
    

class UnloadingBase:
    def __init__(self, env: simpy.Environment, statistic: Statistic):
        self.env = env
        self.statistic = statistic
        self.unloading_points = simpy.Resource(env, capacity=BASE_UNLOADING_POINTS_COUNT)
        self.cranes = simpy.Resource(env, capacity=BASE_CRANES_COUNT)
        self.forklifts = simpy.Resource(env, capacity=BASE_FORKLIFTS_COUNT)
            
    def wait_unloading_point(self, column: Column, statistic: Statistic):
        for truck in column.trucks:
            yield self.env.timeout(1)
            unloading = self.unloading_points.request()
            yield unloading
            self.env.process(self.unload_truck(truck, column, unloading))

    def unload_truck(self, truck, column, unloading):
        forklift = crane = None
        unloading_start = self.env.now
        if truck in COLUMN_TRUCKS_TYPES_REQUIRES_CRANE:
            crane = self.cranes.request()
            self.statistic.set_crane_work_start(crane)
            yield crane
        if truck in COLUMN_TRUCKS_TYPES_REQUIRES_FORKLIFT:
            forklift = self.forklifts.request()
            self.statistic.set_forklift_unload_start(forklift)
            yield forklift

        self.statistic.set_technic_queue(len(self.cranes.queue) + len(self.forklifts.queue))
        time_exponenta = COLUMN_TRUCKS_TYPES_UNLOADING_PARAMS[truck]
        unloading_time = numpy.random.exponential(time_exponenta)
        yield self.env.timeout(unloading_time)
        
        column.unloaded_truck()
        yield self.env.timeout(1)
        self.statistic.truck_unloads_times.append(self.env.now - unloading_start)
        self.unloading_points.release(unloading)
        if truck in COLUMN_TRUCKS_TYPES_REQUIRES_CRANE:
            self.cranes.release(crane)
            self.statistic.set_crane_unload_finish(crane)
        if truck in COLUMN_TRUCKS_TYPES_REQUIRES_FORKLIFT:
            self.statistic.set_forklift_unload_finish(forklift)
            self.forklifts.release(forklift)
        self.statistic.set_unloading_queue(len(self.unloading_points.queue))
        self.statistic.set_technic_queue(len(self.cranes.queue) + len(self.forklifts.queue))
        
    
def modeling(env: simpy.Environment, statistic: Statistic):
    base = UnloadingBase(env, statistic)
    while True:
        column = Column(env, statistic)
        print(f'Колонна №{column.id} прибыла')
        env.process(base.wait_unloading_point(column, statistic))
        next_arrival_time = int( numpy.random.exponential(COLUMN_COLUMN_BASE_ARRIVAL_TIME_DIFFERENS_PARAM) )
        yield env.timeout(next_arrival_time)
        
env = simpy.Environment()
statistic1 = Statistic(env)
env.process(modeling(env, statistic1))
env.run(until=BASE_MODELLING_TIME)
statistic1.print_mean_statistic()

prev_forklifts = BASE_FORKLIFTS_COUNT
BASE_FORKLIFTS_COUNT = 1
Column.GLOBAL_COLUMN_COUNT = 0
print(f'Уменьшили количество форклифтеров до {BASE_FORKLIFTS_COUNT}')
env = simpy.Environment()
statistic2 = Statistic(env)
env.process(modeling(env, statistic2))
env.run(until=BASE_MODELLING_TIME)

t, pval = ttest_ind(
    [x[1] for x in statistic1.unloading_queue_times],
    [x[1] for x in statistic2.unloading_queue_times],
    random_state=1,
    alternative='less'
)
if pval < ALPHA:
    print('Отвергаем нулевую гипотезу о равенстве среднего размера очереди. Принимаем гипотезу, что средний размер очереди во втором эксперименте увеличлся')
else:
    print('Нет оснований отвергать гипотезу о равенстве средних размеров очереди в первом и втором эксперименте')
plt.plot([
    x[0] for x in statistic1.mean_unloading_queue_times], 
    [x[1] for x in statistic1.mean_unloading_queue_times], 
    label=f'forklifts={prev_forklifts}'
)
plt.plot(
    [x[0] for x in statistic2.mean_unloading_queue_times], 
    [x[1] for x in statistic2.mean_unloading_queue_times], 
    label=f'forklifts={BASE_FORKLIFTS_COUNT}'
)
plt.legend()
plt.show()


BASE_FORKLIFTS_COUNT = prev_forklifts
prev_arrival_interval = COLUMN_COLUMN_BASE_ARRIVAL_TIME_DIFFERENS_PARAM
COLUMN_COLUMN_BASE_ARRIVAL_TIME_DIFFERENS_PARAM //= 2
Column.GLOBAL_COLUMN_COUNT = 0
print(f'Уменьшили интервал времени прибытия до {COLUMN_COLUMN_BASE_ARRIVAL_TIME_DIFFERENS_PARAM}')
env = simpy.Environment()
statistic3 = Statistic(env)
env.process(modeling(env, statistic3))
env.run(until=BASE_MODELLING_TIME)

t, pval = ttest_ind(
    [x[1] for x in statistic1.unloading_queue_times],
    [x[1] for x in statistic3.unloading_queue_times],
    random_state=1,
    alternative='less'
)
if pval < ALPHA:
    print('Отвергаем нулевую гипотезу о равенстве среднего размера очереди. Принимаем гипотезу, что средний размер очереди во втором эксперименте увеличлся')
else:
    print('Нет оснований отвергать гипотезу о равенстве средних размеров очереди в первом и втором эксперименте')
plt.plot(
    [x[0] for x in statistic1.mean_unloading_queue_times], 
    [x[1] for x in statistic1.mean_unloading_queue_times], 
    label=f'arrival_interval={prev_arrival_interval}'
)
plt.plot(
    [x[0] for x in statistic3.mean_unloading_queue_times], 
    [x[1] for x in statistic3.mean_unloading_queue_times], 
    label=f'arrival_interval={COLUMN_COLUMN_BASE_ARRIVAL_TIME_DIFFERENS_PARAM}'
)
plt.legend()
plt.show()
