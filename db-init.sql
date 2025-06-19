# Инициализация базы данных помещений
create table if not exists rooms (
	id uuid primary key,
	rtsp text,
	title text
)

# Инициализация базы данных статистики
create table if not exists statistics (
	id uuid primary key,
	work_stations integer,
    persons integer,
    sitting_persons integer,
    not_sitting_persons integer,
    free_work_station integer,
    timestamp timestamp,
    room_id uuid,
    FOREIGN KEY (room_id) REFERENCES rooms (id)
)