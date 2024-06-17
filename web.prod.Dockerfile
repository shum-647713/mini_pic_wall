FROM python:3.12-bookworm

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

COPY manage.py .
COPY mini_pic_wall ./mini_pic_wall

RUN useradd --system --home-dir $HOME app
RUN chown --recursive app $HOME
USER app
