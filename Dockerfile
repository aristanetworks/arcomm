FROM ubuntu:latest

RUN \
  apt-get update && \
  apt-get -y upgrade && \
  apt-get install -y build-essential && \
  apt-get install -y build-essential libssl-dev libffi6 libffi-dev && \
  apt-get install -y libfreetype6 libfreetype6-dev pkg-config && \
  apt-get install -y python3.5 python3.5-dev python3-pip && \
  apt-get install -y libncurses5-dev && \
  pip3 install --upgrade pip && \
  pip3 install future && \
  pip3 install pytest && \
  pip3 install jinja2 && \
  pip3 install pyyaml && \
  pip3 install cryptography --force-reinstall && \
  pip3 install paramiko && \
  pip3 install requests && \
  pip3 install sh && \
  pip3 install ipython jupyter && \
  pip3 install Sphinx

VOLUME ["/arcomm" , "/notebooks"]

WORKDIR /arcomm
#RUN \
#  if [ -e setup.py ]; then python3 setup.py develop

#CMD ["jupyter", "notebook", "--no-broswer", "--ip='*'"]
CMD ["bash"]

#EXPOSE 8888
