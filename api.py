from fastapi import FastAPI, Response, status
from redis_client import redis_client
from postgres_client import postgres_client
import cv2
import numpy as np
from typing import List
from pathlib import Path


app = FastAPI()


@app.get("/rooms")
def get_all_rooms(response: Response):
    cursor = postgres_client.cursor()
    cursor.execute("select * from rooms")
    rooms = cursor.fetchall()

    if not rooms:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"data": None}
    else:
        response.status_code = status.HTTP_200_OK

        def get_room(data):
            return {
                "id": data[0],
                "rtsp": data[1],
                "title": data[2],
            }

        rooms = list(map(get_room, rooms))

        return {"data": rooms}


@app.get("/rooms/{id}")
def get_rooms(id: str, response: Response):
    data = redis_client.hgetall(f'rooms:{id}')

    if not data:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {"data": None}
    else:
        response.status_code = status.HTTP_200_OK
        return {"data": data}


@app.get("/statistics/{id}")
def get_rooms(id: str, response: Response):
    cursor = postgres_client.cursor()

    cursor.execute("select * from work_stations where room_id = %s", (id,))

    work_stations = cursor.fetchall()

    cursor.execute("SELECT work_station_id, ROUND(100.0 * SUM(CASE WHEN free THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) AS free, ROUND(100.0 * SUM(CASE WHEN NOT free THEN 1 ELSE 0 END) / COUNT(*)::numeric, 2) AS busy FROM work_stations_statistics GROUP BY work_station_id;")

    statistics = cursor.fetchall()

    # === Загрузка готового изображения ===
    image_path = Path(f"./rooms/{id}.jpg")  # замените на свой путь
    image = cv2.imread(str(image_path))

    if image is None:
        return Response(content="Image not found", media_type="text/plain", status_code=404)

    img_height, img_width = image.shape[:2]

    # === Рисуем bounding box'ы ===
    for idx in range(0, len(work_stations)):
        box = work_stations[idx]

        work_station_id, x_center, y_center, w, h, room_id, title = box

        abs_x = int(x_center * img_width)
        abs_y = int(y_center * img_height)
        abs_w = int(w * img_width)
        abs_h = int(h * img_height)

        x1 = int(abs_x - abs_w / 2)
        y1 = int(abs_y - abs_h / 2)
        x2 = int(abs_x + abs_w / 2)
        y2 = int(abs_y + abs_h / 2)

        stat = None

        for stat_item in statistics:
            if stat_item[0] == work_station_id:
                stat = stat_item
                break

        stat_str = f"Свобдно: {stat[1]}%, Занято: {stat[2]}%" if stat else "Нет данных"

        color = (0, 255, 0)  # синий по умолчанию
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        lines = [
            f"{title}",
            f"Свобдно: {stat[1]}%" if stat else "Нет данных о времени простоя",
            f"Занято: {stat[2]}%" if stat else "Нет данных  о времени занятости",
        ]

        line_height = 40

        x, y = x1 + 10, y1 + line_height
        for i, line in enumerate(lines):
            y_pos = y + i * line_height
            cv2.putText(image, line, (x, y_pos), cv2.FONT_HERSHEY_COMPLEX,
                        1.3, color, 2)

    # === Кодируем и возвращаем ===
    _, img_encoded = cv2.imencode('.jpg', image)
    return Response(content=img_encoded.tobytes(), media_type="image/jpeg")
