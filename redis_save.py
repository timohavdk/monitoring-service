from redis_client import redis_client
from consumer import consumer


def save():
    for message in consumer:
        if message.value:
            print(f"Принято: {message.value}")

            data = message.value

            if 'room_id' not in data:
                continue

            id = data['room_id']

            room_key = f'rooms:{id}'

            redis_client.hset(room_key, mapping=data)


save()
