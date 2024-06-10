FROM python:3.5

# Install sbt
RUN apt-get update && \
  apt-get install -yqq apt-transport-https && \
  echo "deb https://dl.bintray.com/sbt/debian /" | tee -a /etc/apt/sources.list.d/sbt.list && \
  apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 642AC823 && \
  apt-get update && \
  apt-get -yqq install default-jre sbt

WORKDIR /py4jdbc/
COPY py4jdbc/scala ./py4jdbc/scala
RUN cd /py4jdbc/py4jdbc/scala && sbt clean

COPY . ./
RUN python setup.py build sdist
RUN cd /py4jdbc/dist && pip install py4jdbc-0.1.6.8.tar.gz
ENV CLASSPATH=/usr/local/share/py4jdbc/py4jdbc-assembly-0.1.6.8.jar
