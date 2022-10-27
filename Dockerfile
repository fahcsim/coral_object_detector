FROM ubuntu:20.04
RUN mkdir /python
WORKDIR /python
COPY requirements.txt /tmp/requirements.txt
RUN apt update && apt install curl vim git gnupg2 -y
RUN echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" |  tee /etc/apt/sources.list.d/coral-edgetpu.list && \
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg |  apt-key add - && \
apt-get update  && apt-get install python3-pycoral -y
RUN apt install python3-pip -y
RUN python3 -m pip install -r /tmp/requirements.txt
ENTRYPOINT [ "python3", "/python/detect.py"]