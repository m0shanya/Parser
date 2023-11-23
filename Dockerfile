FROM python:3.10.6-alpine as builder

WORKDIR /usr/src/parser

COPY Pipfile.lock Pipfile ./

RUN apk --no-cache add \
    gcc\
    jpeg-dev\
    libc-dev\
    libffi-dev\
    musl-dev\
    python3-dev\
    zlib-dev\
    && pip3 install pipenv\
    && pipenv requirements > requirements.txt\
    && pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/parser/wheels -r requirements.txt

FROM python:3.10.6-alpine

ENV USER=Parser \
    PYTHONFONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN mkdir -p /home/$USER  \
    && addgroup -S $USER && adduser -S $USER -G $USER

ENV HOME=/home/$USER
ENV APP_HOME=/home/$USER/parser
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

COPY --from=builder /usr/src/parser/wheels /wheels
COPY --from=builder /usr/src/parser/requirements.txt .
RUN pip install --no-cache-dir /wheels/*

COPY . $APP_HOME

RUN chown -R $USER:$USER $APP_HOME
USER $USER

RUN chmod +x $APP_HOME/fastapi-entrypoint.sh
