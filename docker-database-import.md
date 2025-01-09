# Command to import database backup into persistent volume of existing database in PostGres container

`docker exec -i pigskinpredictor-database-1 pg_restore --verbose --clean --no-acl --no-owner -h localhost -U postgres -d default < ./path/to/backup.dump`