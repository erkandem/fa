# https://stackoverflow.com/a/25307587/10124294

# Base Image
FROM python:3.7.9-slim
# Add non-root user, who is going to operate the application
RUN groupadd -r pilot &&\
    useradd -r -g pilot -d /home/pilot -s /sbin/nologin -c "docker application non-root user" pilot

# paths and environment variables
ENV HOME=/home/pilot
ENV APP_HOME=$HOME/ivolapi
WORKDIR $APP_HOME
ENV WHEELS_FOLDER=$APP_HOME/wheels
COPY wheels $WHEELS_FOLDER

# set and create the virtual environment
ENV VIRTUAL_ENV=$APP_HOME/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# install python dependencies wich would require
# extra dependencies
RUN pip install $WHEELS_FOLDER/orjson-3.4.6-cp37-cp37m-manylinux2014_x86_64.whl &&\
    pip install $WHEELS_FOLDER/httptools-0.0.13-cp37-cp37m-linux_x86_64.whl

# install all other requirments
COPY requirements.in requirements.txt requirements-dev.in requirements-docker.txt $APP_HOME/
RUN pip install -r requirements.txt


# application code
COPY falib $APP_HOME/falib
COPY src $APP_HOME/src
COPY appconfig.py $APP_HOME
COPY app.py $APP_HOME
COPY run.sh $APP_HOME
COPY .env.docker $APP_HOME/.env

# switch to non root user
USER pilot

# expose needed ports
EXPOSE 5000

# entrypoint which also laods env vars
CMD ["/bin/bash", "./run.sh"]

# further reading at: gunicorn
# https://docs.gunicorn.org/en/stable/design.html
# https://docs.gunicorn.org/en/stable/configure.html#configuration
# https://docs.gunicorn.org/en/stable/settings.html#settings
# https://docs.gunicorn.org/en/stable/run.html


# docker build -f dockerfiles/app/Dockerfile -t ivolapi:slim-nonroot-4.0.0 .
# docker run -p 5000:5000 --restart unless-stopped -d ivolapi:slim-nonroot-4.0.0
# docker run -p 5000:5000 ivolapi:slim-nonroot-2020
