FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG HOME
ARG APP_HOME
ARG STATIC_FILES
ARG MEDIA_FILES
ARG UPLOAD_IMAGES

WORKDIR $APP_HOME

RUN pip install --upgrade pip
RUN pip install pipenv
RUN pip install flake8
COPY . .
# Прогоняю код через установленный выше линтер flake8.
# Сканирование позволяет обнаружить синтаксические ошибки, несоответствие
# PEP-8 и т.д. Если проверка не пройдена - контейнер не запустится!
RUN flake8 --ignore=E501,F401 .

COPY Pipfile .
COPY Pipfile.lock .

RUN cd $APP_HOME && pipenv install --system --deploy --ignore-pipfile

FROM builder
# Вместо builder (alias на образ выше) можно указать другой образ

ARG HOME
ARG APP_HOME
ARG STATIC_FILES
ARG MEDIA_FILES
ARG UPLOAD_IMAGES

RUN mkdir -p $HOME

RUN adduser --system --group app

RUN mkdir -p $APP_HOME
RUN mkdir -p $STATIC_FILES
RUN mkdir -p $MEDIA_FILES
RUN mkdir -p $UPLOAD_IMAGES

WORKDIR $APP_HOME

RUN apt-get update

COPY ./app $APP_HOME

RUN chown -R app:app $APP_HOME

RUN chmod +x ./scripts/entrypoint.prod.sh

USER app

ENTRYPOINT ["/home/app/backend/scripts/entrypoint.prod.sh"]
