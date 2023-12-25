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

prev_cranes = setts.BASE_CRANES_COUNT
setts.BASE_CRANES_COUNT *= 3
TrucksColumn.GLOBAL_COLUMN_COUNT = 0
print(f'Увеличили количество кранов до {setts.BASE_CRANES_COUNT}')
env = simpy.Environment()
statistic2 = Statistic(env)
env.process(model_base(env, statistic2))
env.run(until=setts.MODELLING_TIME)

t, pval = ttest_ind(
    [x[1] for x in statistic1.technic_queue_time],
    [x[1] for x in statistic2.technic_queue_time],
    random_state=1,
    alternative='greater'
)
if pval < setts.ALPHA:
    print('Отвергаем нулевую гипотезу о равенстве среднего размера очереди в ожидании техники. \
          Принимаем гипотезу, что средний размер очереди ожидания техники во втором эксперименте уменьшился')
else:
    print('Нет оснований отвергать гипотезу о равенстве средних размеров очереди ожидания техники в первом и втором эксперименте')
plt.plot([
    x[0] for x in statistic1.mean_technic_queue], 
    [x[1] for x in statistic1.mean_technic_queue], 
    label=f'cranes={prev_cranes}'
)
plt.plot(
    [x[0] for x in statistic2.mean_technic_queue], 
    [x[1] for x in statistic2.mean_technic_queue], 
    label=f'cranes={setts.BASE_CRANES_COUNT}'
)
plt.legend()
plt.show()


setts.BASE_CRANES_COUNT = prev_cranes
prev_column_trucks = setts.COLUMN_TRUCKS_TYPES_SAME_PARAMS_MATHEXP
setts.COLUMN_TRUCKS_TYPES_SAME_PARAMS_MATHEXP //= 2
TrucksColumn.GLOBAL_COLUMN_COUNT = 0
print(f'Уменьшили количество фур одного типа до {setts.COLUMN_TRUCKS_TYPES_SAME_PARAMS_MATHEXP}')
env = simpy.Environment()
statistic3 = Statistic(env)
env.process(model_base(env, statistic3))
env.run(until=setts.MODELLING_TIME)

t, pval = ttest_ind(
    [x[1] for x in statistic1.technic_queue_time],
    [x[1] for x in statistic3.technic_queue_time],
    random_state=1,
    alternative='greater'
)
if pval < setts.ALPHA:
    print('Отвергаем нулевую гипотезу о равенстве среднего размера очереди в ожидании техники. Принимаем гипотезу, что средний размер очереди ожидания техники во втором эксперименте уменьшился')
else:
    print('Нет оснований отвергать гипотезу о равенстве средних размеров очереди ожидания техники в первом и втором эксперименте')
plt.plot(
    [x[0] for x in statistic1.mean_technic_queue], 
    [x[1] for x in statistic1.mean_technic_queue], 
    label=f'column_trucks={prev_column_trucks}'
)
plt.plot(
    [x[0] for x in statistic3.mean_technic_queue], 
    [x[1] for x in statistic3.mean_technic_queue], 
    label=f'column_trucks={setts.COLUMN_TRUCKS_TYPES_SAME_PARAMS_MATHEXP}'
)
plt.legend()
plt.show()

