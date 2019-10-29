# https://stackoverflow.com/a/25307587/10124294

# Base Image
FROM python:3.7.3-slim
RUN mkdir -p /home/pilot
# Create an app user 'pilot' so our program doesn't run as root.
RUN groupadd -r pilot &&\
    useradd -r -g pilot -d /home/pilot -s /sbin/nologin -c "Docker image user" pilot

# Set the home directory to our app user's home.
ENV HOME=/home/pilot
ENV APP_HOME=/home/pilot/fa

# SETTING UP THE APP ##
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# set the application directory such that the
# pip install is skipped if requirements don't change
ADD requirements-docker.txt $APP_HOME/requirements.txt
RUN chown -R pilot:pilot $HOME
USER pilot
RUN pip install --user -r requirements.txt
ADD ./app.py $APP_HOME
RUN mkdir $APP_HOME/src/
ADD src $APP_HOME/src/
RUN mkdir $APP_HOME/falib
ADD ./falib/* $APP_HOME/falib/
ADD ./.env.docker $APP_HOME/.env

USER root
RUN chown -R pilot:pilot $HOME
USER pilot
EXPOSE 5000


ENV PATH='/home/pilot/.local/bin':$PATH

CMD ["uvicorn", "app:app"]
# further reading at: gunicorn
# https://docs.gunicorn.org/en/stable/design.html
# https://docs.gunicorn.org/en/stable/configure.html#configuration
# https://docs.gunicorn.org/en/stable/settings.html#settings
# https://docs.gunicorn.org/en/stable/run.html

# docker build -t <image_name>:<tag> .
# docker build -t api20:slim-nonroot .

# docker run -p 127.0.0.1:8050:5000 --restart unless-stopped -d api20:slim-nonroot
# docker run -p 127.0.0.1:8050:5000 api20:slim-nonroot --env-file='/home/pilot/api20/.env'
