## To test locally:
# docker build -t proto-builder-1001:0.1.0 .
## 这个dockerfile 用于生成在cosmos module 中处理 proto 的那个镜像
## 用于 替代 cosmos-sdk 的 proto-build 镜像
## 用法: 主要是ARG UID=1001 这一行  将UID 改为 对应的 宿主机 实用用户的UID

FROM bufbuild/buf:1.24.0 as BUILDER
FROM golang:1.21-alpine

RUN apk add --no-cache \
    nodejs \
    npm \
    git \
    make \
    clang-extra-tools \
    g++ \
    jq

RUN npm install -g swagger-combine

ARG UNAME=protobuild
ARG UID=1001
RUN adduser -u $UID -s /bin/sh $UNAME -D && \
    echo "$UNAME ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
USER $UNAME

ENV GOLANG_PROTOBUF_VERSION=1.28.1 \
    GRPC_GATEWAY_VERSION=1.16.0

RUN go install github.com/cosmos/cosmos-proto/cmd/protoc-gen-go-pulsar@latest && \
    go install google.golang.org/protobuf/cmd/protoc-gen-go@v${GOLANG_PROTOBUF_VERSION} && \
    go install github.com/grpc-ecosystem/grpc-gateway/protoc-gen-grpc-gateway@v${GRPC_GATEWAY_VERSION} \
    github.com/grpc-ecosystem/grpc-gateway/protoc-gen-swagger@v${GRPC_GATEWAY_VERSION} && \
    go install cosmossdk.io/orm/cmd/protoc-gen-go-cosmos-orm@v1.0.0-beta.3 && \
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# install all gogo protobuf binaries
RUN git clone https://github.com/cosmos/gogoproto.git; \
    cd gogoproto; \
    go mod download; \
    make install

COPY --from=BUILDER /usr/local/bin /usr/local/bin


