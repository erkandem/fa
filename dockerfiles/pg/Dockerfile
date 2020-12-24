FROM postgres:13.1-alpine
ENV POSTGRES_PASSWORD=postgres
COPY init.sql /docker-entrypoint-initdb.d/

# docker build  -t fastapi_2020_postgres .
# docker run -p 5433:5432 -v fastapi_2020_postgres:/var/lib/postgresql/data fastapi_2020_postgres postgres -c log_statement=all
# psql -U fastapi_2020 -h localhost -p 5433 fastapi_2020
