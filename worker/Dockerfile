FROM hdgigante/python-opencv:4.9.0-alpine

RUN apk add --no-cache \
    git \
    ghostscript-dev \
    build-base \
    openblas-dev \
    libffi-dev
RUN pip install --upgrade pip
COPY ./requirements.txt ./requirements.txt
COPY ./app /app
RUN pip install -r ./requirements.txt
RUN mkdir /data
RUN mkdir /data/jobs
RUN mkdir /data/result
CMD ["python3", "/app/process_book.py"]
