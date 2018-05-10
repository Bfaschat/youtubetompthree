FROM node:7.7.2-alpine
RUN set -x \
 && apk add --no-cache ca-certificates curl ffmpeg python gnupg
WORKDIR /code
COPY ./package.json /code
RUN npm install --quiet
COPY . /code