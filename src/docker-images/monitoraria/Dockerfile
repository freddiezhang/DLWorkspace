
FROM ubuntu:16.04

RUN apt-get update; apt-get install python3 -y

WORKDIR /monitoraria
COPY get-pip.py /monitoraria
COPY six-1.10.0-py2.py3-none-any.whl /monitoraria
RUN python3 get-pip.py
RUN pip install six-1.10.0-py2.py3-none-any.whl

COPY ariapython /ariapython

CMD ["python3", "-m", "monitor.run.py"]

