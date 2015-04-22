#!/usr/bin/env python
from fabric.api import *
from fabric.context_managers import env

#these are the ip addresses of our raspberry pis
env.hosts = ['192.168.0.12', '192.168.0.13','192.168.0.14']
env.password="raspberry"
env.user ="pi"

#update
#lets get these systems ready for action
#will run sudo apt-get update && sudo apt-get upgrade on our pi
@parallel
def update():
    with settings(prompts={'Do you want to continue [Y/n]? ': 'Y'}):
        sudo("apt-get update")
        sudo("apt-get upgrade")
#hadoop
#setting up java, hadoop on the pis
#instuctions originally from https://raspberrypicloud.wordpress.com/2013/04/25/getting-hadoop-to-run-on-the-raspberry-pi/
#adjust this for package location
@parallel
def hadoop():
    with settings(prompts={'Do you want to continue [Y/n]? ': 'Y'}):
        sudo("apt-get install openjdk-7-jdk")
        sudo("addgroup hadoop")
        sudo("adduser --ingroup hadoop hduser")
        sudo("adduser hduser sudo")
        with settings(prompts={'Enter new UNIX password: ': 'raspberry','Retype new UNIX password: ': 'raspberry'}):
            sudo("passwd hduser")
        sudo("ssh-keygen -t rsa -P '' ")
        run("wget http://apache.mirror.vexxhost.com/hadoop/core/hadoop-2.6.0/hadoop-2.6.0.tar.gz")
        sudo("tar vxzf hadoop-2.6.0.tar.gz -C /usr/local")
        sudo("mv /usr/local/hadoop-2.6.0 /usr/local/hadoop")
        sudo("chown -R hduser:hadoop /usr/local/hadoop")
@parallel
def add_path():
    with settings(sudo_user="hduser",user="hduser",prompt={"Enter  ?" :"\r\n"}):   
        sudo ("echo 'export JAVA_HOME=/usr/lib/jvm/java-7-openjdk-armhf' > ~/.bashrc")
        sudo("echo 'export HADOOP_INSTALL=/usr/local/hadoop' >> ~/.bashrc")
        sudo("echo 'export PATH=$PATH:$HADOOP_INSTALL/bin'  >> ~/.bashrc")
        sudo("echo 'export HADOOP_COMMON_LIB_NATIVE_DIR=/usr/local/hadoop/lib/native'  >> ~/.bashrc")
    reboot()        
#setup_ssh_access
#this allows the master, here the first node in hosts to access to the other worker nodes, without requiring passwords every time
#requires user intervention, entering in passwords for slaves
@hosts(env.hosts[0])
def setup_ssh_access():
    with settings(sudo_user="hduser",user="hduser",prompt={"Enter  ?" :"\r\n"}):
        sudo("ssh-keygen -t rsa -P '' ")
        run("eval `ssh-agent`")
        for node in env.hosts[1:]:
            run("ssh-copy-id -i /home/hduser/.ssh/id_rsa.pub hduser@"+node)
        
#hadoop_config
#this sets up the hadoop scratch space
@parallel
def hadoop_config():
    sudo("mkdir -p /fs/hadoop/tmp")
    sudo("chown hduser:hadoop /fs/hadoop/tmp")
    sudo("sudo chmod 750 /fs/hadoop/tmp")

#install_spark
#installs spark, change url and folder to match version
@parallel
def install_spark():
    run("wget http://d3kbcqa49mib13.cloudfront.net/spark-1.3.1-bin-hadoop2.6.tgz")
    run("tar -xf spark-1.3.1-bin-hadoop2.6.tgz")
    run("mv ./spark-1.3.1-bin-hadoop2.6 ./spark")
#copy over conf files
@parallel
def configure_single_hadoop():
    puts('./core-site.xml' , '/usr/local/hadoop/etc/hadoop/')
    puts('./mapred-site.xml' , '/usr/local/hadoop/etc/hadoop/')
    puts('./yarn-site.xml' , '/usr/local/hadoop/etc/hadoop/')
    puts('./hdfs-site.xml' , '/usr/local/hadoop/etc/hadoop/')
    with settings(sudo_user="hduser",user="hduser",prompt={"Enter  ?" :"\r\n"}):
        run('mkdir -p /home/hduser/storage/hadoop/namenode/')
        run('mkdir -p /home/hduser/storage/hadoop/datanode/')
#check hadoop single node
@parallel
def check_single_hadoop():
    with settings(sudo_user="hduser",user="hduser",prompt={"Enter  ?" :"\r\n"}):
        run("/usr/local/hadoop/bin/hadoop namenode -format")
        run("/usr/local/hadoop/bin/start-all.sh")
@hosts(env.hosts[0])
def init_hdfs()
    for host in env.hosts[1:]:
        with open('slaves', 'a') as f:
            f.write(str(host))
    puts("./slaves", "/usr/local/hadoop/etc/hadoop")
    run("hdfs namenode -format ")
