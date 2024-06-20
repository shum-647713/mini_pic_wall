FROM python:3.12-alpine

ENV HOME=/home/app
RUN mkdir -p $HOME
RUN mkdir $HOME/static
RUN mkdir $HOME/media
WORKDIR $HOME

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT ["/home/app/entrypoint.sh"]
