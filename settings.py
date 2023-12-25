
# Параметры количества типов грузовиков в одной колонне. Триугольный закон~~~~~~~~~~~~~~~~~
COLUMN_MIN_TRUCKS = 4
COLUMN_MAX_TRUCKS = 10
COLUMN_MODE_TRUCKS = 8

# Параметры количество фур одного типа в колонне. Нормальный закон распределения~~~~~~~~~~~
COLUMN_TRUCKS_TYPES_SAME_PARAMS_MATHEXP = 14
COLUMN_TRUCKS_TYPES_SAME_PARAMS_STDEVIATION = 3 

# Параметры генерации времени разгрузки фур по типу. Экспоненциальный закон~~~~~~~~~~~~~~~
TRUCK_TYPES_MATHEXPS = [22, 21, 27, 24, 17, 19, 22, 31, 28, 29]

# Типы фур требующие технику для разгрузки~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
TRUCK_REQUIRES_FORKLIFT_PROBABILITY = 0.4
TRUCK_REQUIRES_CRANE_PROBABILITY = 0.3

# Количество техники и точек разгрузки~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
BASE_FORKLIFTS_COUNT = 3
BASE_CRANES_COUNT = 2
BASE_UNLOADING_POINTS_COUNT = 10

# Стартегия выбора точки для разгрузки. В данном случае реализовано random или sequintial~~
# В случае random точка разгрузки выбирается случайно из свободных
# В случае sequintial точка разгрузки выбирается первая свободная по порядку

BASE_UNLOADING_CHOICE_STRATEGY = 'random'

# Параметр времени прибытия фур на базу (в минутах). Экспоненциальный закон распределения~~
ARRIVAL_TIME_DIFFERENS_PARAM = 540

# Время симуляции~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
MODELLING_TIME = 43200

# Параметры отрисовки статистики~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
DRAW_EXPERIMENT = False
DRAW_TEXT_STAT = True if not DRAW_EXPERIMENT else False
DRAW_DYNAMIC_GRAPH = False if not DRAW_EXPERIMENT else True
PLOT_RATE = 100


ALPHA = 0.05