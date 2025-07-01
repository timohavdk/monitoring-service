import math


def center_distance_ratio(center1, center2, base_length=1.0):
    """
    Вычисляет расстояние между двумя центрами и нормализует его в долях от base_length.

    :param center1: первый центр (x, y)
    :param center2: второй центр (x, y)
    :param base_length: базовая длина (например, ширина или диагональ изображения)
    :return: расстояние и расстояние в долях (от 0 до 1)
    """
    dx = center1[0] - center2[0]
    dy = center1[1] - center2[1]
    dist = math.sqrt(dx**2 + dy**2)

    ratio = dist / base_length if base_length != 0 else 0
    return ratio
