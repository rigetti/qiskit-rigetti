FROM python:3.7-slim

ARG DEBIANP_FRONTEND=noninteractive
ARG USERNAME=qiskit_user
ARG USER_UID=1000
ARG USER_GID=1000

ENV POETRY_HOME=/opt/poetry

# Install OS requirements
RUN apt update && \
    apt install -y bash-completion curl git

# Install python requirements
RUN pip install tox && \
    curl -sSL https://install.python-poetry.org | python3 -

ENV PATH=${POETRY_HOME}/bin:$PATH

RUN useradd --uid 1000 $USERNAME && \
    mkdir -p /home/${USERNAME}/.vscode-server /home/${USERNAME}/.vscode-server-insiders && \
    (chown ${USER_UID}:${USER_GID} /home/${USERNAME}/.vscode-server*)

USER ${USERNAME}
WORKDIR /qiskit_rigetti

CMD [ "/bin/bash" ]