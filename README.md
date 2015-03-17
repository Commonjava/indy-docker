# Docker Utilities and Image Files for AProx

This repository contains a set of init scripts for setting up aprox docker containers of three flavors:

  * A stripped-down volumes container (`init-aprox-volumes`)
  * An AProx server container meant to work with the volume container (`init-aprox-server`)
  * A standalone AProx server container (`init-aprox-server-no-vols`)

It also contains systemd scripts for maintaining active AProx containers, one apiece corresponding to the 
init scripts above.

Finally, it contains the docker image source materials (Dockerfile + supporting scripts) for the two basic
image types (server and volume container).

## Quickstart for CentOS 7

This is intended to be more or less a list of instructions for you to run. It would take a bit more effort
to turn it into a really functional script:

    #!/bin/bash
    
    yum -y update
    yum -y install docker tree lsof
    systemctl enable docker
    systemctl start docker
    curl http://repo.maven.apache.org/maven2/org/commonjava/aprox/docker/aprox-docker-utils/0.19.1/aprox-docker-utils-0.19.1.tar.gz | tar -zxv
    cd aprox-docker-utils
    
    ./init-aprox-volumes
    
    # You might want to edit the port envar or some of the other options 
    # in this script before executing. When you execute, wait for the server
    # to indicate that it's running, hit CTL-C, and proceed below.
    ./init-aprox-server
    
    cp systemd/aprox-volumes.service systemd/aprox-server.service /etc/systemd/system
    systemctl enable aprox-volumes aprox-server
    
    docker stop aprox aprox-volumes
    systemctl start aprox-volumes
    systemctl start aprox
    
    # Use this to see the server log as it starts up, to make sure it boots properly.
    journalctl -f

