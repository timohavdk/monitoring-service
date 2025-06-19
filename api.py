from fastapi import FastAPI, Response, status
from redis_client import redis_client
from postgres_client import postgres_client


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
