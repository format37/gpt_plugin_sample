FROM python:3.10-slim-buster
WORKDIR /worker
COPY requirements.txt /worker
RUN pip3 install -r requirements.txt --no-cache-dir
COPY server.py /worker
ENTRYPOINT ["python3"]
CMD ["server.py"]

