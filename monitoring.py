import cv2
import time
import multiprocessing
from datetime import datetime, timedelta
from ultralytics import YOLO
from analyze_room import AnalyzerRoom
from producer import producer


class Monitoring:
    def __init__(self, rooms, topic, dev=False):
        self.rooms = rooms
        self.topic = topic
        self.dev = dev

    def _read_rtsp(self, rtsp_url, frame_queue):
        cap = cv2.VideoCapture(rtsp_url)

        if not cap.isOpened():
            print(f"[{rtsp_url}] Не удалось открыть поток")
            return

        while True:
            ret, frame = cap.read()

            if self.dev:
                time.sleep(1)

            if ret:
                if not frame_queue.empty():
                    try:
                        frame_queue.get_nowait()
                    except:
                        pass

                frame_queue.put(frame)

    def _process_frame(self, room_id, topic, frame_queue):
        model = YOLO('./yolos/yolo-n.pt')
        analyzer = AnalyzerRoom(min_conf=0.5)
        prod = producer

        while True:
            if not frame_queue.empty():
                start = datetime.now()
                frame = frame_queue.get()
                timestamp = datetime.now().isoformat()

                results = model(frame, verbose=False)
                statistics = analyzer.analyze(
                    results[0].boxes.cpu().numpy())

                stop = datetime.now()
                print(f'Processed: {room_id} - {start} - {stop - start}')

                data = {**statistics, 'timestamp': timestamp, 'room_id': room_id}

                prod.send(topic, data)

            time.sleep(10)

    def _monitoring(self, room):
        rtsp = room['rtsp']
        room_id = room['id']

        frame_queue = multiprocessing.Queue(maxsize=1)

        reader = multiprocessing.Process(
            target=self._read_rtsp, args=(rtsp, frame_queue))
        processor = multiprocessing.Process(
            target=self._process_frame, args=(room_id, self.topic, frame_queue))

        reader.start()
        processor.start()

        return [reader, processor]

    def start(self, demo=True):
        if demo:
            print('demo')

            rtsp = self.rooms[0]['rtsp']
            room_id = self.rooms[0]['id']
            cap = cv2.VideoCapture(rtsp)

            if not cap.isOpened():
                print("Не удалось открыть видео")
                exit()

            fps = cap.get(cv2.CAP_PROP_FPS)               # Частота кадров
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            # Продолжительность видео в секундах
            duration = frame_count / fps

            print(
                f"FPS: {fps}, Всего кадров: {frame_count}, Длительность: {duration:.2f} сек")

            # Интервал между кадрами (в секундах)
            interval = 10

            # Чтение кадров с шагом
            sec = 0
            frame_id = 0

            now = datetime.now()
            start_time = datetime(now.year, now.month, now.day, 8, 0)

            while sec < duration:
                frame_number = int(sec * fps)
                # Перемещаемся на нужный кадр
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
                success, frame = cap.read()

                if success:
                    model = YOLO('./yolos/yolo-s.pt')
                    analyzer = AnalyzerRoom(min_conf=0.5)
                    prod = producer

                    timestamp = (start_time +
                                 timedelta(seconds=sec)).isoformat()

                    results = model(frame, verbose=False)
                    statistics = analyzer.analyze(
                        results[0].boxes.cpu().numpy())

                    print(
                        f'Processed: {room_id}')

                    data = {**statistics,
                            'timestamp': timestamp, 'room_id': room_id}

                    prod.send(self.topic, data)

                    # Сохраняем кадр в файл
                else:
                    print(f"Не удалось считать кадр на {sec} сек.")
                sec += interval
                frame_id += 1

            cap.release()
            print("Готово.")

        else:
            processes = []
            for room in self.rooms:
                procs = self._monitoring(room)
                processes.extend(procs)

            for p in processes:
                p.join()
