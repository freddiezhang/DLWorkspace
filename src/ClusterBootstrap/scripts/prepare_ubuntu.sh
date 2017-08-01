#!/bin/bash
# Install python on CoreOS base image
# Docker environment for development of DL workspace
set -e

sudo apt-get update 
sudo apt-get upgrade -y
sudo apt-get -y dist-upgrade
sudo apt-get install -y linux-image-extra-virtual
sudo apt-get install -y --no-install-recommends \
        apt-utils \
        build-essential \
        cmake \
        git \
        curl \
        wget \
        python-dev \
        python-numpy \
        python-pip \
        apt-transport-https \
        ca-certificates \
        vim \
        nfs-common \
        ubiquity
        


sudo apt-get install -y bison curl 

# Install docker
curl -q https://get.docker.com/ | sudo bash

sudo useradd -p saekab9n9hYug -d /home/core -m -s /bin/bash core
echo "core:M$ft2016" | sudo chpasswd
sudo usermod -aG sudo core
sudo mkdir -p /home/core/.ssh
echo ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDDLyQsNU3C6R1N1Uuxcep8cIbQbfpkaNbBxlgLmH4RLQzBlvBqIPjne8S13Dw1DNa4RkyCHmrgbTkRXGAKJxmeNv/N0m8WaZYAIFwL140M+vTLDf6IEQjtUItb6PTEO+HsX8xnuBWh22OlF5n+N3iAnw2bTKlT3TYW/njotp408cmrebEV7wZtNNYbrJgLGyT/uTQe6lRoZ1iCO7ZJHVulAtynGzskYer0zK45FW7FYUJvtdzDN8uM523KfNlNABJxD1kDD7/6RLMur9yOpka6e5V3mAdOwM3lKhV+bwhv+xjg+81vE5g7lFnVg4lj26pWMGlQUYVpoPNjH3BBOAiJD1GbkH1k7RVZFN6M402KB5ZRlfLhvIl32VhS+O5cvN1DFCT0roOcr0gX290aScvPVNRf0AGGvu5XkuT1fxFaaTzz/Yw/PiSlcduaXoWSxpH1i+3GPBvqebnJbWDZaOyhEg0u9zQVzQrc0zF4nk111N7uChE6rTjX4D6wrJi2PRNbXdpesAC9Qa4zSswUywVO6c7gB+5S7SCqU+xwyH7tVDTFuTXOTq9gq1G5wGC3ByYfXlz0to97tLdWbgSlLkaMR8/IQtt+UmxM8OGMZ3T1qF2bJf+z/C7FLpiHiHAjJ//+FFmF1u34jI6JJDNco2M2NtUiCYZxGLqcT/4pW0dpVw== | sudo tee /home/core/.ssh/authorized_keys
sudo chown core:core -R /home/core
sudo chmod 400 /home/core/.ssh/authorized_keys


sudo usermod -aG docker core

echo 'core ALL=(ALL) NOPASSWD: ALL' | sudo tee -a /etc/sudoers.d/core 



sudo add-apt-repository -y ppa:graphics-drivers/ppa
sudo apt-get update
#sudo apt-get install -y --no-install-recommends nvidia-381
sudo apt-get install -y nvidia-381

sudo apt install -y nvidia-modprobe



#wget http://us.download.nvidia.com/XFree86/Linux-x86_64/378.13/NVIDIA-Linux-x86_64-378.13.run
#chmod +x NVIDIA-Linux-x86_64-378.13.run


#https://github.com/NVIDIA/nvidia-docker/issues/137



#sudo cat << EOF > /etc/modprobe.d/blacklist-nouveau.conf
#blacklist nouveau
#options nouveau modeset=0
#EOF

#sudo update-initramfs -u
#sudo apt-get install dkms linux-headers-generic



#NVIDIA_VERSION=378.13

#sudo ./NVIDIA-Linux-x86_64-$NVIDIA_VERSION.run  -q -a -s --dkms \
#    --opengl-libdir=lib64 \
#    --utility-libdir=lib64 \
#    --x-library-path=lib64 \
#    --compat32-libdir=lib \



#NV_DRIVER=/opt/nvidia-driver/$NVIDIA_VERSION
#sudo mkdir -p $NV_DRIVER
#sudo ./NVIDIA-Linux-x86_64-$NVIDIA_VERSION.run  -q -a -s --dkms\
#    --utility-prefix=$NV_DRIVER \
#    --opengl-prefix=$NV_DRIVER \
#    --x-prefix=$NV_DRIVER \
#    --compat32-prefix=$NV_DRIVER \
#    --opengl-libdir=lib64 \
#    --utility-libdir=lib64 \
#    --x-library-path=lib64 \
#    --compat32-libdir=lib \
#    -N 
#sudo ln -s $NV_DRIVER /opt/nvidia-driver/current
#echo /opt/nvidia-driver/current/lib64 | sudo tee /etc/ld.so.conf.d/nvidia.conf
#sudo ldconfig


sudo reboot


cd ~
wget http://ccsdatarepo.westus.cloudapp.azure.com/data/ib/MLNX_OFED_LINUX-4.0-2.0.0.1-ubuntu16.04-x86_64.tgz
tar -zxvf MLNX_OFED_LINUX-4.0-2.0.0.1-ubuntu16.04-x86_64.tgz
cd MLNX_OFED_LINUX-4.0-2.0.0.1-ubuntu16.04-x86_64/
echo "y" | sudo ./mlnxofedinstall
sudo /etc/init.d/openibd restart

sudo cat << EOF | sudo tee -a /etc/network/interfaces
auto ib0
iface ib0 inet static
        address 192.168.1.10
        netmask 255.255.255.0
        network 192.168.1.0
        broadcast 192.168.1.255 
EOF

echo "192.168.1.2:/volumes/vol1     /nfsmnt  nfs     rsize=8192,timeo=14,intr,tcp" | sudo tee -a /etc/fstab




sudo reboot


#sudo cp -r /dlwsdata/storage/sys/nvidia-driver /opt/
#sudo ln -s /opt/nvidia-driver/381.22 /opt/nvidia-driver/current

sudo mkdir -p /nfsmnt
sudo mkdir -p /dlwsdata
sudo mount /nfsmnt || true
sudo rm -r /dlwsdata/storage ; sudo rm -r /dlwsdata/work ; sudo rm -r /dlwsdata/jobfiles || true
sudo ln -s /nfsmnt/data /dlwsdata/storage
sudo ln -s /nfsmnt/users /dlwsdata/work
sudo ln -s /nfsmnt/dlworkspace /dlwsdata/jobfiles





sudo rm -r /opt/nvidia-driver || true

# should NOT install cuda, install cuda will automatically install a older version of nvidia driver
#sudo dpkg -i /dlwsdata/storage/sys/cuda-repo-ubuntu1604-8-0-local-ga2_8.0.61-1_amd64.deb
#sudo apt-get update
#sudo apt-get install -y --no-install-recommends cuda


# Install nvidia-docker and nvidia-docker-plugin
wget -P /tmp https://github.com/NVIDIA/nvidia-docker/releases/download/v1.0.1/nvidia-docker_1.0.1-1_amd64.deb
sudo dpkg -i /tmp/nvidia-docker*.deb && rm /tmp/nvidia-docker*.deb

# Test nvidia-smi
sudo nvidia-docker run --rm nvidia/cuda nvidia-smi

NVIDIA_VERSION=381.22
sudo mkdir -p /opt/nvidia-driver/
sudo cp -r /var/lib/nvidia-docker/volumes/nvidia_driver/* /opt/nvidia-driver/
NV_DRIVER=/opt/nvidia-driver/$NVIDIA_VERSION
sudo ln -s $NV_DRIVER /opt/nvidia-driver/current



sudo mkdir -p /opt/bin
sudo cp /dlwsdata/storage/sys/bin/* /opt/bin/
sudo cp /dlwsdata/storage/sys/hadoop-mount.service /etc/systemd/system
sudo systemctl start hadoop-mount
sudo systemctl enable hadoop-mount

