FROM python:3.11.9

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG REQUIREMENTS_FILE

COPY ./$REQUIREMENTS_FILE ./

RUN pip install --upgrade pip
RUN pip install -r $REQUIREMENTS_FILE --no-cache-dir
RUN mkdir logs
RUN mkdir logs/backend
RUN mkdir logs/nginx

COPY . /app

COPY ./entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

EXPOSE 8000