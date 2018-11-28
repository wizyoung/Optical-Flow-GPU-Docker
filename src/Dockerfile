FROM willprice/opencv2-cuda8

COPY . .

RUN apt-get -y update \
    && apt-get install -y \
        libboost-all-dev \
        unzip \
        libzip-dev \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get autoclean \
    && apt-get autoremove

WORKDIR /src
RUN git clone --recursive http://github.com/yjxiong/dense_flow \
    && cd dense_flow \
    && mkdir build && cd build \
    && cmake .. && make -j \
    && cp /src/dense_flow/build/extract* /usr/bin/ \
    && rm -rf /src/dense_flow /src/opencv* 