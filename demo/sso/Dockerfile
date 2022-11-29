FROM python:3.6.8

WORKDIR /app

COPY . .

RUN pip3 --disable-pip-version-check install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

CMD ["python3", "app.py"]
