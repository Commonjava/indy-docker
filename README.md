# Docker Utilities and Image Files for AProx

This repository contains a set of init scripts for setting up aprox docker containers of three flavors:

  * A stripped-down volumes container (`init-aprox-volumes`)
  * An AProx server container meant to work with the volume container (`init-aprox-server`)
  * A standalone AProx server container (`init-aprox-server-no-vols`)

You can run any of the above scripts with `-h` to see the available options.

It also contains an autodeploy script (`autodeploy-aprox-server`) that you can add to your cron jobs, 
to autodeploy an AProx tarball in dev-mode. Systemd scripts are provided in the `systemd/` directory, 
for maintaining active AProx containers, with one service definition for each of the init scripts above.

Finally, it contains the docker image source materials (Dockerfile + supporting scripts) for the two basic
image types (server and volume container).

## Quickstart for CentOS 7

This is intended to be more or less a list of instructions for you to run. It would take a bit more effort
to turn it into a really functional script:

    #!/bin/bash
    
    yum -y update
    yum -y install epel-release
    yum -y install docker tree lsof python-lxml python-httplib2
    systemctl enable docker
    systemctl start docker
    curl http://repo.maven.apache.org/maven2/org/commonjava/aprox/docker/aprox-docker-utils/0.19.1/aprox-docker-utils-0.19.1.tar.gz | tar -zxv
    cd aprox-docker-utils
    
    # ./init-aprox-volumes -h
    ./init-aprox-volumes
    
    # ./init-aprox-server -h
    ./init-aprox-server -p 80 -q
    
    #Or, if you want, you can leave off the '-q' option and watch the server come up
    #...then use CTL-C to exit the tty (the container will keep running)
    
    cp systemd/aprox-volumes.service systemd/aprox-server.service /etc/systemd/system
    systemctl enable aprox-volumes aprox-server
    
    docker stop aprox aprox-volumes
    systemctl start aprox-volumes
    systemctl start aprox
    
    # Use this to see the server log as it starts up, to make sure it boots properly.
    journalctl -f

