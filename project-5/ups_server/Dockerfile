FROM ubuntu:16.04

RUN mkdir /ups_code
RUN apt-get update && apt-get -y install python3
RUN apt-get update && apt-get -y install python3-pip
RUN python3 -m pip install threadpool
RUN python3 -m pip install google
RUN python3 -m pip install six
RUN python3 -m pip install psycopg2-binary==2.7.7
RUN python3 -m pip install protobuf

WORKDIR /ups_code
ADD . /ups_code
EXPOSE 6666
CMD python3 /ups_code/server_ups.py