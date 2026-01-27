FROM python:3.10

WORKDIR /app
COPY . .

RUN apt-get update && apt-get install -y default-mysql-client pdftk-java
RUN python -m pip install --upgrade pip setuptools
RUN pip install -r requirements.txt
RUN chmod +x run.sh

EXPOSE 9000
CMD ["./run.sh"]
