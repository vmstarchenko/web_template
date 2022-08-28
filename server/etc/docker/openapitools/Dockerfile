FROM docker.io/openapitools/openapi-generator-cli

RUN useradd --create-home --shell /bin/bash --home /home/user user
USER user
WORKDIR /home/user

COPY ./config-typescript-axios.yaml ./etc/config-typescript-axios.yaml
