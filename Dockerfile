FROM ubuntu
COPY . /app
WORKDIR "/app"
RUN yes | unminimize
RUN apt update
RUN apt -y install bash curl git manpages-posix manpages-dev manpages-posix-dev man-db python3 python3-pip
RUN python3 -m pip install tox
RUN python3 -m pip install .
