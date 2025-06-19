from kafka import KafkaConsumer
import json
from dotenv import load_dotenv
import os
import json

load_dotenv()

topic = os.getenv("TOPIC")

consumer = KafkaConsumer(
    topic,
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)
