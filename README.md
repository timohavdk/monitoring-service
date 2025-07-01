# Сервис мониторинга использования рабочих мест

Для запуска:

1. Миграции

```sh
python migrate.py
```

2. Запуск анализа видеопотоков из rooms.yaml

```sh
python main.py
```

3. Сохранение в postgre sql

```sh
python postgres_save.py
```

4. Сохранение в redis

```sh
python redis_save.py
```

5. Запуск API

```sh
uvicorn api:app
```

6. Grafana

Используется конфигурация `grafana-config.json`

Модели yolo находятся в директории `yolo`, нужная указывается в `monitoring.py`
