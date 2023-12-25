from trucks import TrucksColumn
from base import Base
from statistic import Statistic
from numpy import random
import settings as setts
import simpy
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

def model_base(env: simpy.Environment, statistic: Statistic):
    base = Base(env, statistic)
    while True:
        column = TrucksColumn(env, statistic)
        env.process(base.wait_unloading_point(column))
        next_arrival_time = int( random.exponential(setts.ARRIVAL_TIME_DIFFERENS_PARAM) )
        yield env.timeout(next_arrival_time)
        

env = simpy.Environment()
statistic1 = Statistic(env)
env.process(model_base(env, statistic1))
env.run(until=setts.MODELLING_TIME)
statistic1.print_mean_statistic()
statistic1.print_workload_statistic()

prev_forklifts = setts.BASE_FORKLIFTS_COUNT
setts.BASE_FORKLIFTS_COUNT = 1
TrucksColumn.GLOBAL_COLUMN_COUNT = 0
print(f'Уменьшили количество форклифтеров до {setts.BASE_FORKLIFTS_COUNT}')
env = simpy.Environment()
statistic2 = Statistic(env)
env.process(model_base(env, statistic2))
env.run(until=setts.MODELLING_TIME)

t, pval = ttest_ind(
    [x[1] for x in statistic1.unloading_queue_times],
    [x[1] for x in statistic2.unloading_queue_times],
    random_state=1,
    alternative='less'
)
if pval < setts.ALPHA:
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
    label=f'forklifts={setts.BASE_FORKLIFTS_COUNT}'
)
plt.legend()
plt.show()


setts.BASE_FORKLIFTS_COUNT = prev_forklifts
prev_arrival_interval = setts.ARRIVAL_TIME_DIFFERENS_PARAM
setts.ARRIVAL_TIME_DIFFERENS_PARAM //= 2
TrucksColumn.GLOBAL_COLUMN_COUNT = 0
print(f'Уменьшили интервал времени прибытия до {setts.ARRIVAL_TIME_DIFFERENS_PARAM}')
env = simpy.Environment()
statistic3 = Statistic(env)
env.process(model_base(env, statistic3))
env.run(until=setts.MODELLING_TIME)

t, pval = ttest_ind(
    [x[1] for x in statistic1.unloading_queue_times],
    [x[1] for x in statistic3.unloading_queue_times],
    random_state=1,
    alternative='less'
)
if pval < setts.ALPHA:
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
    label=f'arrival_interval={setts.ARRIVAL_TIME_DIFFERENS_PARAM}'
)
plt.legend()
plt.show()

