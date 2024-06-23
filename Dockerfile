from python:3.10

workdir /app

run pip install --upgrade pip

copy requirements.txt /app/
run pip3 install -r requirements.txt

copy . /app/
