FROM python:3.10
WORKDIR /TalkTrain
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .

