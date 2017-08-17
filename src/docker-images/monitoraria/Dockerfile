
FROM ubuntu:16.04

RUN apt-get update; apt-get install -y python3-dev python3-pip
RUN pip3 install --upgrade pip; pip3 install setuptools six requests

WORKDIR /monitoraria
# ADD get-pip.py /monitoraria
# ADD six-1.10.0-py2.py3-none-any.whl /monitoraria
# RUN python3 get-pip.py
# RUN pip install six-1.10.0-py2.py3-none-any.whl

ADD ariapython /monitoraria

CMD ["python3", "-m", "monitor.run.py"]

