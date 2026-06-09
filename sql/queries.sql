select * from flight;

select * from hotel;

select * from weather;

alter table weather
add column location varchar(30);

alter table hotel
modify airport varchar(5);

alter table hotel
rename column airport to close_to_airport;

alter table hotel
add column location varchar(30);

Truncate table flight;
truncate table hotel;
truncate table weather;