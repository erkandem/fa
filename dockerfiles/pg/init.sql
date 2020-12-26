-- every user should have it's own database, which has the same name as the user
CREATE DATABASE fastapi_2020;
CREATE ROLE fastapi_2020 WITH PASSWORD 'postgres';

-- set some default which will prevent lookup queries and therefore speed up all queries
-- source https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04
ALTER ROLE fastapi_2020 SET client_encoding TO 'utf8';
ALTER ROLE fastapi_2020 SET default_transaction_isolation TO 'read committed';
ALTER ROLE fastapi_2020 SET timezone TO 'UTC';
ALTER ROLE fastapi_2020 WITH LOGIN;
ALTER ROLE fastapi_2020 WITH SUPERUSER;

-- grant rights to read, write, ... and so on
GRANT ALL PRIVILEGES ON DATABASE fastapi_2020 TO fastapi_2020;
ALTER DATABASE fastapi_2020 OWNER TO fastapi_2020;

--
-- testing equivalent
--
CREATE DATABASE fastapi_2020_testing;
CREATE ROLE fastapi_2020_testing WITH PASSWORD 'postgres';

-- set some default which will prevent lookup queries and therefore speed up all queries
-- source https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04
ALTER ROLE fastapi_2020_testing SET client_encoding TO 'utf8';
ALTER ROLE fastapi_2020_testing SET default_transaction_isolation TO 'read committed';
ALTER ROLE fastapi_2020_testing SET timezone TO 'UTC';
ALTER ROLE fastapi_2020_testing WITH LOGIN;
ALTER ROLE fastapi_2020_testing WITH SUPERUSER;

-- grant rights to read, write, ... and so on
GRANT ALL PRIVILEGES ON DATABASE fastapi_2020_testing TO fastapi_2020_testing;
ALTER DATABASE fastapi_2020 OWNER TO fastapi_2020;
