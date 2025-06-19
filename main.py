from monitoring import Monitoring
import yaml
from yaml.loader import SafeLoader
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    topic = os.getenv("TOPIC")

    confing_file = 'rooms.yaml'
    rooms_key = 'rooms'

    rooms = []
    with open(confing_file, 'r') as f:
        data = list(yaml.load_all(f, Loader=SafeLoader))
        if data and rooms_key in data[0]:
            rooms = data[0][rooms_key]
        else:
            print("Файл rooms.yaml не содержит данных")

    monitoring = Monitoring(rooms, topic, dev=True)
    monitoring.start()
