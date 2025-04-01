FROM python:3.8-slim

RUN apt update && apt install -y awscli less

WORKDIR /workspace
VOLUME /workspace

RUN python -m venv venv
ENV PATH="/workspace/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --prefer-binary -r requirements.txt

COPY fetch-notebook.sh .
COPY publish-result.py .
COPY script.sh .
COPY notify-teams.py .
COPY notify-lailo.py .
COPY notify-telegram.py .
COPY custom_logger.py .

RUN chmod +x fetch-notebook.sh \
    && chmod +x script.sh \
    && chmod +x *.py

RUN mkdir tmp

ENV DOCKER_ENV=1
ENV IPYTHONDIR=/workspace/.ipython
ENV MPLCONFIGDIR=/workspace/.matplotlib

CMD ./script.sh
