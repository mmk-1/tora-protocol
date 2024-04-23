# Download base image ubuntu 22.04
FROM ubuntu:22.04
# LABEL about the custom image
LABEL maintainer="ertan.onur@arleon.com.tr"
LABEL version="0.1"
LABEL description="This is AHC development environment"

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

# Update Ubuntu Software repository
RUN apt update

RUN apt -y install  openvswitch-switch \
    python3 \
    python3-pip \
    build-essential \
    git \
    texlive-latex-extra \
    latexmk \
    locales

RUN locale-gen en_US.UTF-8 && \
    echo "LANG=en_US.UTF-8" > /etc/default/locale

RUN git clone https://github.com/cengwins/ahc && \
    cd ahc && \
    pip3 install -r requirements.txt

RUN pip3 install adhoccomputing

ENV HOME /root

# WORKDIR /root

# COPY . .

# WORKDIR /root/code

CMD ["sleep", "infinity"]