ARG BUILD_FROM
FROM $BUILD_FROM

WORKDIR /app

# Install requirements for add-on
RUN apk update && apk add --no-cache python3 py3-pip build-base python3-dev

COPY . /app/

RUN bash build.sh

RUN chmod +x run.sh
CMD [ "./run.sh" ]