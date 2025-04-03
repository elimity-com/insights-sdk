FROM node:lts
ARG TARGETARCH
ENV PATH=$PATH:/root/go/bin:/usr/local/go/bin
RUN \
    curl -L https://go.dev/dl/go1.24.1.linux-$TARGETARCH.tar.gz | tar -C /usr/local -xz && \
    curl https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh && \
    go install github.com/jdeflander/goarrange@latest
