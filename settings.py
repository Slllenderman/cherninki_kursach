
# Параметры прибытия автомобилей (мин макс мода) Триангулярный закон распределения~~~~~~~~~
COLUMN_MIN_TRUCKS = 4
COLUMN_MAX_TRUCKS = 10
COLUMN_MODE_TRUCKS = 8

# Параметры генерации типов фур в колонне. Нормальный закон распределения~~~~~~~~~~~~~~~~~~
COLUMN_TRUCKS_TYPES_COUNT = 10
COLUMN_TRUCKS_TYPES_SAME_PARAMS_MATHEXP = 14
COLUMN_TRUCKS_TYPES_SAME_PARAMS_STDEVIATION = 3 

# Параметры генерации времени разгрузки фур по типу. Экспоненциальный закон распределения~~
COLUMN_TRUCKS_TYPES_UNLOADING_PARAMS = [22, 21, 27, 24, 17, 19, 22, 31, 28, 29]

# Параметр времени прибытия фур на базу (в минутах). Экспоненциальный закон распределения~~
COLUMN_ARRIVAL_TIME_DIFFERENS_PARAM = 540

# Типы фур требующие технику для разгрузки~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
COLUMN_TRUCKS_TYPES_REQUIRES_FORKLIFT = [0, 1, 2, 3]
COLUMN_TRUCKS_TYPES_REQUIRES_CRANE = [7, 8, 9]

# Дополнительные параметры симуляции~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
BASE_FORKLIFTS_COUNT = 10
BASE_CRANES_COUNT = 10
BASE_UNLOADING_POINTS_COUNT = 10
BASE_MODELLING_TIME = 43200