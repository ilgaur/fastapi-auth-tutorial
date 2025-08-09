# Ubuntu/Debian
sudo apt update && sudo apt install postgresql postgresql-contrib

# Start PostgreSQL and create database
sudo -u postgres psql
CREATE DATABASE auth_tutorial;
CREATE USER username WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE auth_tutorial TO username;
\q

# Or via Docker
docker run --name postgres-auth -e POSTGRES_DB=auth_tutorial -e POSTGRES_USER=username -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:13