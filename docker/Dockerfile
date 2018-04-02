FROM ubuntu:xenial-20180228

RUN apt-get -y update && \
    apt-get -y install --no-install-recommends apt-utils && \
    apt-get -y install --no-install-recommends \
        apt-transport-https \
        binutils \
        build-essential \
        ca-certificates \
        curl \
        default-jre \
        git \
        git-core \
        htop \
        jove \
        less \
        libffi-dev \
        libkrb5-dev \
        libmysqlclient-dev \
        libpq-dev \
        libsasl2-dev \
        libssl-dev \
        libxml2-dev \
        libxslt-dev \
        logrotate \
        mysql-client \
        net-tools \
        netcat \
        openssh-server \
        parallel \
        python3 \
        python3-dev \
        rsync \
        ssh-client \
        sudo \
        supervisor \
        telnet \
        tmux \
        tree \
        unixodbc \
        unixodbc-dev \
        unzip \
        vim \
        wget && \
    useradd -ms /bin/bash -d ${AIRFLOW_HOME} airflow && \
    addgroup wheel && \
    adduser airflow wheel && \
    echo "%wheel        ALL=(ALL)       NOPASSWD: ALL" > /etc/sudoers.d/wheel && \
    chmod 0440 /etc/sudoers.d/wheel && \
    apt-get -y autoclean && \
    apt-get -y clean && \
    apt-get -y autoremove && \
    rm -frv /var/lib/apt/lists/*

