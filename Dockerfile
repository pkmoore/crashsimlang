FROM ubuntu
COPY . /app
WORKDIR "/app"
RUN yes | unminimize
RUN apt update
RUN apt -y install bash python3 python3-pip curl git manpages-posix manpages-dev manpages-posix-dev man-db python3-distutils python3-apt
RUN python3 -m pip install tox .
