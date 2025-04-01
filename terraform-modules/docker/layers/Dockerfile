FROM amazonlinux:latest

RUN yum install -y make tar gzip wget gcc openssl-devel bzip2-devel libffi-devel  zlib-devel zip

ENV PYTHON_VER=3.9.12
RUN wget https://www.python.org/ftp/python/${PYTHON_VER}/Python-${PYTHON_VER}.tgz
RUN tar xzf Python-${PYTHON_VER}.tgz && rm Python-${PYTHON_VER}.tgz
WORKDIR Python-${PYTHON_VER}
RUN ./configure --enable-optimizations
RUN make altinstall
RUN ln -s /usr/local/bin/python3.9 /usr/local/bin/python3
RUN ln -s /usr/local/bin/pip3.9 /usr/local/bin/pip3
RUN rm -rf Python-${PYTHON_VER}


ENV TERRAFORM_VER=1.9.3
RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VER}/terraform_${TERRAFORM_VER}_linux_amd64.zip
RUN yum -y install unzip
RUN unzip terraform_${TERRAFORM_VER}_linux_amd64.zip && \
    mv terraform /usr/local/bin

WORKDIR /root/context
