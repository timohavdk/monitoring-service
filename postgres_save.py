from postgres_client import postgres_client
from consumer import consumer
from uuid import uuid4


def save():
    cursor = postgres_client.cursor()

    try:
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
    except:
        print("Произошла ошибка при сохранении данных в базу")

        cursor.close()


save()
