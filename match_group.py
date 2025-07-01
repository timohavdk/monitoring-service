import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment


def match_group(group_A, group_B):
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
