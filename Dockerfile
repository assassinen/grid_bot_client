FROM python:3.7.2

RUN mkdir -p /grid_client
WORKDIR /grid_client
COPY . /grid_client
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD python3 run.py