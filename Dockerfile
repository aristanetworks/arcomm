FROM alpine:edge

RUN \
  apk update && \
  apk upgrade && \
  apk add bash git && \
  apk add python3 py3-paramiko && \
  pip3 install --upgrade pip && \
  pip3 install future && \
  pip3 install pytest && \
  pip3 install jinja2 && \
  pip3 install pyyaml && \
  pip3 install requests && \
  pip3 install sh && \
  git clone https://github.com/aristanetworks/arcomm.git /arcomm


VOLUME ["/arcomm"]

ENV PYTHONPATH /arcomm

WORKDIR /arcomm

ENTRYPOINT ["python3.6", "/arcomm/arcomm/entry.py"]
