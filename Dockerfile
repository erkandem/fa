# https://stackoverflow.com/a/25307587/10124294

# Base Image
FROM python:3.7-slim
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
# install local wheels to avoid GCC error form debian slim image
RUN mkdir $APP_HOME/wheels
ADD wheels/httptools-0.0.13-cp37-cp37m-linux_x86_64.whl $APP_HOME/wheels/httptools-0.0.13-cp37-cp37m-linux_x86_64.whl
RUN pip install --user $APP_HOME/wheels/httptools-0.0.13-cp37-cp37m-linux_x86_64.whl

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
ADD appconfig.py $APP_HOME/appconfig.py
USER root
RUN chown -R pilot:pilot $HOME
USER pilot
EXPOSE 5000

ENV PATH='/home/pilot/.local/bin':$PATH

CMD ["/home/pilot/.local/bin/uvicorn", "app:app", "--host", "0.0.0.0", "--port", "5000", "--env-file", ".env"]

# further reading at: gunicorn
# https://docs.gunicorn.org/en/stable/design.html
# https://docs.gunicorn.org/en/stable/configure.html#configuration
# https://docs.gunicorn.org/en/stable/settings.html#settings
# https://docs.gunicorn.org/en/stable/run.html

# docker build -t <image_name>:<tag> .
# docker build -t fast-api:slim-nonroot .

# docker run -p 127.0.0.1:5000:5000 --restart unless-stopped -d fast-api:slim-nonroot
# docker run -p 127.0.0.1:5000:5000 fast-api:slim-nonroot
