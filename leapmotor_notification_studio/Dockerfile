ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache libjpeg-turbo zlib freetype
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
COPY rootfs/app /app
COPY rootfs/run.sh /
RUN chmod a+x /run.sh
WORKDIR /app
CMD [ "/run.sh" ]
