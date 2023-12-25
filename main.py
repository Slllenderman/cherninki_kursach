from trucks import TrucksColumn
from base import Base
from statistic import Statistic
from numpy import random
import settings as setts
import simpy


def model_base(env: simpy.Environment, statistic: Statistic):
    base = Base(env, statistic)
    while True:
        column = TrucksColumn(env, statistic)
        env.process(base.wait_unloading_point(column))
        next_arrival_time = int( random.exponential(setts.ARRIVAL_TIME_DIFFERENS_PARAM) )
        yield env.timeout(next_arrival_time)
        

env = simpy.Environment()
statistic = Statistic(env)
env.process(model_base(env, statistic))
env.run(until=setts.MODELLING_TIME)

statistic.print_mean_statistic()
statistic.print_workload_statistic()