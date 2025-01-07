ARG IMAGE
FROM ${IMAGE}
ARG IMAGE
ARG PIP
ARG PYTHON_VERSION

RUN if echo ${IMAGE} | grep -q "amazon"; then \
      # Amazon Linux doesn't have rsyslog installed by default
      yum update -y && yum install -y python3-pip rsyslog; \
    elif echo ${IMAGE} | grep -q "centos"; then \
      curl https://bootstrap.pypa.io/pip/2.7/get-pip.py --output get-pip.py && \
      python get-pip.py; \
    elif echo ${IMAGE} | grep -q "osx"; then \
        python -m ensurepip; \
    fi

RUN ${PIP} install pytest

# Only install black on Python 3.x as it doesn't exist on 2.x
RUN if [ $PYTHON_VERSION -ge 3 ]; then ${PIP} install black isort; fi

WORKDIR /app
