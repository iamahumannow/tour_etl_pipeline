select * from flight;

select * from hotel;

select * from weather;

alter table hotel
rename column Aiport to airport;

alter table weather
modify decimal(3,1);

Truncate table flight;
truncate table hotel;
truncate table weather;