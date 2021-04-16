FROM fnndsc/irtk:1.0

RUN apt-get update \
  && apt-get install -y python3-pip \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/local/src

COPY . .
RUN pip3 --no-cache-dir install .

CMD ["irtkrecon", "--help"]
