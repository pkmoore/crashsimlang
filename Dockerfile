FROM ubuntu
COPY . /app
WORKDIR "/app"
RUN yes | unminimize
RUN apt update
RUN apt -y install bash python2 curl git manpages-posix manpages-dev manpages-posix-dev man-db
RUN curl https://bootstrap.pypa.io/2.7/get-pip.py --output get-pip.py
RUN python2 get-pip.py
RUN pip install tox
RUN pip install .
