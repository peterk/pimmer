#FROM python:3.6-alpine
FROM nuveo/opencv:alpine-python3-opencv3
RUN apk add --no-cache git ghostscript-dev
RUN pip install --upgrade pip
COPY ./requirements.txt ./requirements.txt
COPY ./app /app
RUN pip install -r ./requirements.txt
RUN mkdir /data
RUN mkdir /data/jobs
RUN mkdir /data/result
CMD ["python", "/app/process_book.py"]
