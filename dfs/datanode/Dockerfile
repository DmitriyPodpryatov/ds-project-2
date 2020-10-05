FROM python:3.8-slim

WORKDIR /datanode
COPY . /datanode

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 7777

CMD ["python", "datanode.py"]
