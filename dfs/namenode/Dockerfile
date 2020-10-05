FROM python:3.8-slim

WORKDIR /namenode
COPY . /namenode

RUN pip install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 5555

CMD ["python", "namenode.py"]
