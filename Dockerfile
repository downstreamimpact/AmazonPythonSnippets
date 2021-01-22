FROM lambci/lambda:build-python3.7

WORKDIR /var/task
COPY requirements.txt ./

RUN pip3 install -r requirements.txt
