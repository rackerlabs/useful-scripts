FROM centos:7
RUN yum install -y python3
RUN yum install -y perl
RUN yum install -y which
RUN yum install -y curl
RUN yum install -y net-tools
RUN yum install -y procps
RUN yum install -y httpd
RUN yum install -y httpd-tools
ENTRYPOINT /usr/sbin/httpd -k start && curl -sk https://raw.githubusercontent.com/richardforth/apache2buddy/staging/apache2buddy.pl | perl
