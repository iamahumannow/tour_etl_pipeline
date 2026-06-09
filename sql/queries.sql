select * from flight;

select * from hotel;

select * from weather;

select * from monthly_flight;

select * from monthly_hotel;

select * from monthly_weather;

select * from best_time;

describe monthly_weather;

alter table best_time
add column fetched_at datetime;

alter table monthly_weather
modify location varchar(35) NULL;

alter table hotel
rename column airport to close_to_airport;

alter table monthly_hotel
add column location varchar(30);

Truncate table flight;
truncate table hotel;
truncate table weather;
truncate table monthly_flight;
truncate table monthly_hotel;
truncate table monthly_weather;
truncate table best_time;