FROM node:lts-trixie
ENV PATH=$PATH:/root/.local/bin:/root/go/bin
RUN \
    apt-get update && apt-get install -y golang && \
    curl https://golangci-lint.run/install.sh | sh && \
    curl https://install.python-poetry.org | python3 && \
    go install github.com/bufbuild/buf/cmd/buf@latest && \
    go install github.com/jdeflander/goarrange@latest
