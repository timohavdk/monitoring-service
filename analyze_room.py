import numpy as np
import ultralytics
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment
from match_group import match_group


class AnalyzerRoom():
    CLASSES = {
        'work_station': 80,
        'person':       0,
    }

    def __init__(self, min_conf: float = 0.5):
        self.min_conf = min_conf

    def __center(self, x1: int, y1: int, x2: int, y2: int):
        x = x1 + ((x2 - x1) / 2)
        y = y1 + ((y2 - y1) / 2)

        return (x, y)

    def __is_sitting(self, person: np.ndarray, work_station: np.ndarray):
        x1 = max(person[0], work_station[0])
        y1 = max(person[1], work_station[1])
        x2 = min(person[2], work_station[2])
        y2 = min(person[3], work_station[3])

        inter_width = max(0, x2 - x1)
        inter_height = max(0, y2 - y1)
        inter_area = inter_width * inter_height

        inner_area = (person[2] - person[0]) * (person[3] - person[1])

        # Чтобы избежать деления на 0
        if inner_area == 0:
            return 0, 0

        ratio = inter_area / inner_area

        return ratio > 0.8

    def __result(
        self,
        work_stations:       int,
        persons:             int,
        sitting_persons:     int,
        not_sitting_persons: int,
        free_work_station:   int,
        work_stations_collect,
    ):
        result = {
            'work_stations':         int(work_stations),
            'persons':               int(persons),
            'sitting_persons':       int(sitting_persons),
            'not_sitting_persons':   int(not_sitting_persons),
            'free_work_station':     int(free_work_station),
            'work_stations_collect': work_stations_collect,
        }

        return result

    def __clear_work_stations(self, work_stations, orig_shape):
        orig_height, orig_width = orig_shape[0], orig_shape[1]

        items = []

        for idx in range(0, len(work_stations)):
            work_station = work_stations[idx]

            x_1, y_1, x_2, y_2 = work_station[0] / orig_width, work_station[1] / \
                orig_height, work_station[2] / \
                orig_width, work_station[3] / orig_height

            width = x_2 - x_1
            height = y_2 - y_1
            x_center = x_1 + (width / 2)
            y_center = y_1 + (height / 2)

            data = [float(x_center), float(y_center),
                    float(width), float(height), False]

            items.append(data)

        return items

    def __work_stations(self, pairs, persons, work_stations, orig_shape):
        items = self.__clear_work_stations(work_stations, orig_shape)

        for i, j in pairs:
            items[j][4] = not bool(self.__is_sitting(
                persons[i], work_stations[j]))

        return items

    def analyze(self, data: ultralytics.engine.results.Boxes):
        def get_filter_function(class_code: int):
            def filter_function(
                x): return x[5] == class_code and x[4] >= self.min_conf

            return filter_function

        work_station_filter_function = get_filter_function(
            AnalyzerRoom.CLASSES['work_station']
        )

        person_filter_function = get_filter_function(
            AnalyzerRoom.CLASSES['person']
        )

        all_class = data.data

        work_stations = list(filter(work_station_filter_function, all_class))
        persons = list(filter(person_filter_function, all_class))

        if len(work_stations) == 0:
            return self.__result(0, len(persons), 0, len(persons), 0, [])
        elif len(persons) == 0:
            return self.__result(len(work_stations), 0, 0, 0, len(work_stations), self.__clear_work_stations(work_stations, data.orig_shape))

        work_station_centers = list(
            map(lambda x: self.__center(x[0], x[1], x[2], x[3]), work_stations))
        person_centers = list(
            map(lambda x: self.__center(x[0], x[1], x[2], x[3]), persons))

        pairs = match_group(person_centers, work_station_centers)

        sitting = 0

        for i, j in pairs:
            result = self.__is_sitting(persons[i], work_stations[j])

            sitting += result

        not_sitting = len(persons) - sitting
        free_work_station = len(work_stations) - sitting

        new_data = self.__work_stations(
            pairs, persons, work_stations, data.orig_shape)

        return self.__result(len(work_stations), len(persons), sitting, not_sitting, free_work_station, new_data)
