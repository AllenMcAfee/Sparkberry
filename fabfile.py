#!/usr/bin/env python
from fabric.api import *
from fabric.context_managers import env

#these are the ip addresses of our raspberry pis
env.hosts = ['192.168.0.12', '192.168.0.13','192.168.0.14']
env.password="raspberry"
env.user ="pi"

#will run sudo apt-get update && sudo apt-get upgrade on our pi
@parallel
def update():
    with settings(prompts={'Do you want to continue [Y/n]? ': 'Y'}):
        sudo("apt-get update")
        sudo("apt-get upgrade")
        
#setting up java, hadoop on the pis
#instuctions originally from https://raspberrypicloud.wordpress.com/2013/04/25/getting-hadoop-to-run-on-the-raspberry-pi/
@parallel
def hadoop():
    with settings(prompts={'Do you want to continue [Y/n]? ': 'Y'}):
        sudo("apt-get install openjdk-7-jdk")
        sudo("addgroup hadoop")
        sudo("adduser --ingroup hadoop hduser")
        sudo("adduser hduser sudo")
        sudo("ssh-keygen -t rsa -P '' ",user="hduser")
        run("wget http://apache.mirror.vexxhost.com/hadoop/core/hadoop-2.6.0/hadoop-2.6.0.tar.gz")
        sudo("tar vxzf hadoop-2.6.0.tar.gz -C /usr/local")
        sudo("mv /usr/local/hadoop-2.6.0 /usr/local/hadoop")
        sudo("chown -R hduser:hadoop /usr/local/hadoop")
        run("echo 'export JAVA_HOME=/usr/lib/jvm/java-6-openjdk-armhf' > ~/.bashrc")
        run("echo 'export HADOOP_INSTALL=/usr/local/hadoop' >> ~/.bashrc")
        run("echo 'export PATH=$PATH:$HADOOP_INSTALL/bin'  >> ~/.bashrc")
        #reboot()
@parallel
def hadoop_config():
    sudo("mkdir -p /fs/hadoop/tmp")
    sudo("chown hduser:hadoop /fs/hadoop/tmp")
    sudo("sudo chmod 750 /fs/hadoop/tmp")
    run("hadoop namenode -format")