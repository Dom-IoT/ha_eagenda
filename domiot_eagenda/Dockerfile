ARG BUILD_FROM
FROM $BUILD_FROM

RUN apk update && apk add --no-cache \
    python3 \
    py3-pip \
    python3-dev

WORKDIR /app


COPY requirements.txt ./

RUN pip3 install --break-system-packages -r requirements.txt

COPY backend.py backend.py

EXPOSE 8001

COPY run.sh /
RUN chmod a+x /run.sh
CMD [ "/run.sh" ]