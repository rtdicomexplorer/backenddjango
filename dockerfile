FROM python:3:12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

ARG REQUIREMENTS_FILE
#system dependencies for lxml
RUN apt-get update && apt-get install -y \
    libxml2-dev \
    libxslt1-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


COPY ./$REQUIREMENTS_FILE ./

RUN pip install --upgrade pip
RUN pip install -r $REQUIREMENTS_FILE --no-cache-dir --no-compile
RUN mkdir logs
RUN mkdir logs/backend
RUN mkdir logs/frontend
RUN mkdir logs/nginx
RUN mkdir static
RUN mkdir /media/avatars

COPY . /app

COPY ./media/user.png /app/media/user.png

COPY ./entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh

EXPOSE 8000