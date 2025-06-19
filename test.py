from uuid import uuid4

for i in range(10):
    print(
        f'("{uuid4()}", "rtsp://192.168.0.100:8080/h264_ulaw.sdp", "Помещение {i}"),')
