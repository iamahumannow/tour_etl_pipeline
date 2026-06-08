CREATE TABLE IF NOT EXISTS flights (
	id INT AUTO_INCREMENT PRIMARY KEY,
    flight_number varchar(20) not null,
    airline varchar(40),
    airplane varchar(20),
    leg_room varchar(20),
    departure_date date not null,
    departure_time time not null,
    arrival_date date not null,
    arrival_time time not null,
    duration int,
    price decimal(8,2) not null,
    fetched_at datetime not null
    );
    
CREATE TABLE IF NOT EXISTS weather (
	latitude decimal(5,4) not null,
    longitude decimal(5,4) not null,
    elevation decimal (5,1),
    hour_date date not null,
    hour_time time not null,
    hour_temp decimal(2,1) not null,
    hour_precipitation decimal(2,1) not null,
    );
    
CREATE TABLE IF NOT EXISTS hotel (
	hotel_id int auto_increment primary key,
    name varchar(80) not null,
    stay_type varchar(30),
    rating decimal(2,1),
    no_of_people int,
    beds int,
    bedroom int,
    bathroom int,
    check_times varchar(50),
    Aiport bool
    );
    
CREATE TABLE IF NOT EXISTS monthly_hotel (
	months varchar(20),
    price decimal(6,1)
    );
    
CREATE TABLE IF NOT EXISTS monthly_flight (
	months varchar(20),
    price decimal(6,1),
    price_range varchar(15)
    );
    
CREATE TABLE IF NOT EXISTS monthly_weather (
	latitude decimal(5,4) not null,
    longitude decimal(5,4) not null,
    location varchar(25) not null,
    months varchar(20),
    temperature_2m decimal(6,2),
    temperature_2m_max decimal(6,2),
    temperature_2m_min decimal(6,2),
    precipitation decimal(6,2),
    sunshine_duration decimal (5,2)
    );