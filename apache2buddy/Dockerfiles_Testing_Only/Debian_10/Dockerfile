FROM debian:10
RUN  apt-get update
RUN  apt-get -y install curl
RUN  apt-get -y install procps
RUN  apt-get -y install net-tools
RUN  apt-get -y install apache2
RUN  apt-get -y install perl
RUN  apt-get -y install python3
ENTRYPOINT service apache2 start && curl -sk https://raw.githubusercontent.com/richardforth/apache2buddy/staging/apache2buddy.pl | perl
