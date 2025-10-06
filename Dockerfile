FROM node:lts-trixie
ARG TARGETARCH
ENV PATH=$PATH:/root/.local/bin:/root/go/bin:/usr/local/go/bin
RUN \
    curl -L https://go.dev/dl/go1.24.1.linux-$TARGETARCH.tar.gz | tar -C /usr/local -xz && \
    curl https://install.python-poetry.org | python3 && \
    curl https://raw.githubusercontent.com/golangci/golangci-lint/master/install.sh | sh && \
    go install github.com/bufbuild/buf/cmd/buf@latest && \
    go install github.com/jdeflander/goarrange@latest
