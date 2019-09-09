FROM python:3.7.1-stretch

RUN mkdir -p /grid_client
WORKDIR /grid_client
COPY . /grid_client
RUN pip install --no-cache-dir -r requirements.txt

CMD python3 run.py