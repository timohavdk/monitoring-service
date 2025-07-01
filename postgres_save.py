from postgres_client import postgres_client
from consumer import consumer
from uuid import uuid4
from match_group import match_group


def save():
    rooms = {}

    cursor = postgres_client.cursor()

    cursor.execute("select * from work_stations")

    work_stations = cursor.fetchall()

    for work_station in work_stations:
        room_id = work_station[5]

        if room_id not in rooms:
            rooms[room_id] = []

        rooms[room_id].append(work_station)

    for message in consumer:
        print(f"Принято: {message.value}")

        if message.value:
            data = message.value

            if 'room_id' not in data:
                continue

            values = (
                str(uuid4()),
                data['room_id'],
                data['work_stations'],
                data['persons'],
                data['sitting_persons'],
                data['not_sitting_persons'],
                data['free_work_station'],
                data['timestamp'],
            )

            cursor.execute(
                "INSERT INTO statistics (id, room_id, work_stations, persons, sitting_persons, not_sitting_persons, free_work_station, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", values)

            room_id = data['room_id']
            orig_work_stations = rooms[room_id]
            work_stations_collect = data['work_stations_collect']

            if 0 == len(work_stations_collect):
                print(f"Нет рабочих мест для комнаты {room_id}")
                continue

            orig_centers = [(orig_work_station[1], orig_work_station[2])
                            for orig_work_station in orig_work_stations]
            target_centers = [(work_station[0], work_station[1])
                              for work_station in work_stations_collect]

            pairs = match_group(orig_centers, target_centers)

            for pair in pairs:
                cursor.execute(
                    "INSERT INTO work_stations_statistics (id, work_station_id, free, timestamp) VALUES (%s, %s, %s, %s)",
                    (
                        str(uuid4()),
                        str(orig_work_stations[pair[0]][0]),
                        str(work_stations_collect[pair[1]][4]),
                        str(data['timestamp']),
                    )
                )


save()
