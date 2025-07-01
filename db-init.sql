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

# Инициализация базы данных рабочих мест
create table if not exists work_stations (
	id uuid primary key,
	x_center real,
    y_center real,
    width real,
    height real,
    room_id uuid,
)

# Инициализация базы данных статистики рабочих мест
create table if not exists work_stations_statistics (
	id uuid primary key,
    work_station_id uuid,
    free boolean,
    timestamp timestamp,
)