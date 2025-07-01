def compute_iou(box1, box2):
    """
    Вычисляет IoU двух прямоугольников.
    Ожидается формат: [x_center, y_center, width, height] в пикселях или нормализованных координатах.
    """

    # Преобразуем (x_center, y_center, width, height) в (x1, y1, x2, y2)
    def to_corners(box):
        x_center, y_center, width, height = box
        x1 = x_center - width / 2
        y1 = y_center - height / 2
        x2 = x_center + width / 2
        y2 = y_center + height / 2
        return [x1, y1, x2, y2]

    box1 = to_corners(box1)
    box2 = to_corners(box2)

    # Координаты пересечения
    inter_x1 = max(box1[0], box2[0])
    inter_y1 = max(box1[1], box2[1])
    inter_x2 = min(box1[2], box2[2])
    inter_y2 = min(box1[3], box2[3])

    # Площадь пересечения
    inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)

    # Площади прямоугольников
    area_box1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area_box2 = (box2[2] - box2[0]) * (box2[3] - box2[1])

    # IoU
    union_area = area_box1 + area_box2 - inter_area
    iou = inter_area / union_area if union_area != 0 else 0

    return iou
