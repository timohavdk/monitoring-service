import cv2
import time
import threading
import yaml
from datetime import datetime
from yaml.loader import SafeLoader
from analyze_room import MonitoringWorkstations
from ultralytics import YOLO
from producer import producer
from dotenv import load_dotenv
import os


class Monitoring():
    def __init__(self, rooms, topic):
        self.model = YOLO('./yolos/yolo-m.pt')
        self.analyzer = MonitoringWorkstations(min_conf=0.5)
        self.producer = producer
        self.rooms = rooms
        self.topic = topic

    def _process_frame(self, frame, room_id):
        timestamp = datetime.now().isoformat()

        start = datetime.now()
        results = self.model(frame, verbose=False)

        statistics = self.analyzer.get_statistics(
            results[0].boxes.cpu().numpy()
        )

        end = datetime.now()

        print(f"[{room_id}] Обработка кадра заняла {end - start}")

        data = {**statistics, 'timestamp': timestamp, 'room_id': room_id}

        self.producer.send(self.topic, data)

    def _read_stream(self, room):
        id = room['id']
        rtsp = room['rtsp']

        cap = cv2.VideoCapture(rtsp)

        cam_name = f'{id} - {rtsp}'

        if not cap.isOpened():
            print(f"[{cam_name}] Не удалось подключиться")
            return

        print(f"[{cam_name}] Подключение установлено")

        last = time.time()

        retry = 0
        max_retries = 5

        while True:
            ret, frame = cap.read()

            if not ret:
                print(f"[{cam_name}] Ошибка при чтении кадра")

                if retry <= max_retries:
                    retry += 1

                    print(f'retry {retry}')

                    continue
                else:

                    print('breaking')
                    cap.release()
                    break

            now = time.time()

            if now - last >= 10:
                self._process_frame(frame, id)

                last = now

    def start(self):
        threads = []

        for room in self.rooms:
            print(rooms)

            t = threading.Thread(target=self._read_stream, args=(room, ))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()


rooms = []

with open('rooms.yaml', 'r') as f:
    data = list(yaml.load_all(f, Loader=SafeLoader))

    if len(data[0]) != 0:
        rooms = data[0]['rooms']
    else:
        print("Файл rooms.yaml не содержит данных")

load_dotenv()

topic = os.getenv("TOPIC")

monitoring = Monitoring(rooms, topic)

monitoring.start()
