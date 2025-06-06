import numpy as np
import ultralytics
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment


class MonitoringWorkstations():
    OBJECT_CLASSES = {
        'work_station': 80,
        'person':       0,
    }

    def __init__(self, min_conf: float = 0.5):
        self.min_conf = min_conf

    def __get_center(self, x1: int, y1: int, x2: int, y2: int):
        x = x1 + ((x2 - x1) / 2)
        y = y1 + ((y2 - y1) / 2)

        return (x, y)

    def __is_person_sitting_on_work_station(self, person: np.ndarray, work_station: np.ndarray):
        person_center = self.__get_center(
            person[0], person[1], person[2], person[3])

        is_x_include = (
            person_center[0] >= work_station[0] and person_center[0] <= work_station[2])
        is_y_include = (
            person_center[1] >= work_station[1] and person_center[1] <= work_station[3])

        if (not is_x_include) or (not is_y_include):
            return False
        else:
            intersection_s = 0

            start = work_station[0] if person[0] <= work_station[0] else person[0]
            stop = work_station[2] if person[2] >= work_station[2] else person[2]

            width = stop - start

            start = work_station[1] if person[1] <= work_station[1] else person[1]
            stop = work_station[3] if person[3] >= work_station[3] else person[3]

            height = stop - start

            intersection_s = width * height

            person_s = (person[2] - person[0]) * (person[3] - person[1])

            part = (intersection_s / person_s)

            result = part >= 0.8

            return result

    # Венгерский алгоритм
    # TODO детально изучить

    def __match_groups(self, group_A, group_B):
        A = np.array(group_A)
        B = np.array(group_B)
        m, n = len(A), len(B)

        # Вычисляем матрицу расстояний между группами
        cost_matrix = cdist(A, B)  # shape (m, n)

        # Делаем квадратную матрицу путём дополнения
        if m > n:
            # Добавим фиктивные столбцы (нулевые пары, очень большая стоимость)
            pad = np.full((m, m - n), fill_value=1e6)
            cost_matrix = np.hstack([cost_matrix, pad])
        elif n > m:
            # Добавим фиктивные строки
            pad = np.full((n - m, n), fill_value=1e6)
            cost_matrix = np.vstack([cost_matrix, pad])

        # Решаем задачу
        row_ind, col_ind = linear_sum_assignment(cost_matrix)

        # Отбираем только допустимые пары (исключаем фиктивные)
        pairs = []
        for i, j in zip(row_ind, col_ind):
            if i < m and j < n:
                pairs.append((i, j))  # индексы в group_A и group_B

        return pairs

    def __get_result_object(
        self,
        count_work_stations:       int,
        count_persons:             int,
        count_sitting_persons:     int,
        count_not_sitting_persons: int,
        count_free_work_station:   int,
    ):
        result = {
            'count_work_stations':       int(count_work_stations),
            'count_persons':             int(count_persons),
            'count_sitting_persons':     int(count_sitting_persons),
            'count_not_sitting_persons': int(count_not_sitting_persons),
            'count_free_work_station':   int(count_free_work_station),
        }

        return result

    def get_statistics(self, data: ultralytics.engine.results.Boxes):
        def get_filter_function(class_code: int):
            def filter_function(
                x): return x[5] == class_code and x[4] >= self.min_conf

            return filter_function

        work_station_filter_function = get_filter_function(
            MonitoringWorkstations.OBJECT_CLASSES['work_station']
        )

        person_filter_function = get_filter_function(
            MonitoringWorkstations.OBJECT_CLASSES['person']
        )

        all_class = data.data

        work_stations = list(filter(work_station_filter_function, all_class))
        persons = list(filter(person_filter_function, all_class))

        if len(work_stations) == 0:
            return self.__get_result_object(0, len(persons), 0, len(persons), 0)
        elif len(persons) == 0:
            return self.__get_result_object(len(work_stations), 0, 0, 0, len(work_stations))

        work_station_centers = list(
            map(lambda x: self.__get_center(x[0], x[1], x[2], x[3]), work_stations))
        person_centers = list(
            map(lambda x: self.__get_center(x[0], x[1], x[2], x[3]), persons))

        pairs = self.__match_groups(person_centers, work_station_centers)

        count_sitting = 0

        for i, j in pairs:
            result = self.__is_person_sitting_on_work_station(
                persons[i], work_stations[j])

            count_sitting += result

        count_not_sitting = len(persons) - count_sitting
        count_free_work_station = len(work_stations) - count_sitting

        return self.__get_result_object(len(work_stations), len(persons), count_sitting, count_not_sitting, count_free_work_station)
