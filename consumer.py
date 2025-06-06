from kafka import KafkaConsumer
import json
from dotenv import load_dotenv
import os

load_dotenv()

topic = os.getenv("TOPIC")

consumer = KafkaConsumer(
    topic,
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

print("Consumer started...")

for message in consumer:
    # {
    #   'count_work_stations': 0,
    #   'count_persons': 0,
    #   'count_sitting_persons': 0,
    #   'count_not_sitting_persons': 0,
    #   'count_free_work_station': 0,
    #   'timestamp': '2025-06-06T00:24:26.114534',
    #   'room_id': '10'
    # }
    print(f"Consumed: {message.value}")
    
    # Добавить запись в redis
    # Добавить запись в pg
    
    
