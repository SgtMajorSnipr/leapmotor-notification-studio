ARG BUILD_FROM
FROM ${BUILD_FROM}

RUN apk add --no-cache libjpeg-turbo zlib freetype
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir -r /tmp/requirements.txt
COPY rootfs/app /app
WORKDIR /app
CMD ["python3", "-m", "main"]
