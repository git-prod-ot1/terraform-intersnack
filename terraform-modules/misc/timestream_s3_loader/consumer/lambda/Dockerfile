FROM public.ecr.aws/lambda/python:3.11

WORKDIR ${LAMBDA_TASK_ROOT}
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip setuptools wheel && \
    python3 -m pip cache purge && \
    python3 -m pip install --default-timeout=1000 --no-cache-dir -r requirements.txt && \
    rm requirements.txt
ENV PYTHONPATH="${LAMBDA_TASK_ROOT}/:${PYTHONPATH}"
COPY ./src/ .

CMD [ "main.handler" ]
