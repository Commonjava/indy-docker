# Docker Utilities and Image Files for Indy

This repository contains a set of init scripts for setting up indy docker containers of three flavors:

  * A stripped-down volumes container (`init-indy-volumes`)
  * An Indy server container meant to work with the volume container (`init-indy-server`)
  * A standalone Indy server container (`init-indy-server-no-vols`)

You can run any of the above scripts with `-h` to see the available options.

It also contains an autodeploy script (`./scripts/autodeploy-indy-server`) that you can add to your cron jobs, 
to autodeploy an Indy tarball in dev-mode. Systemd scripts are provided in the `systemd/` directory, 
for maintaining active Indy containers, with one service definition for each of the init scripts above.

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
    
    # ./scripts/init-indy-volumes -h
    ./scripts/init-indy-volumes
    
    # ./scripts/init-indy-server -h
    ./scripts/init-indy-server -p 80 -q
    
    #Or, if you want, you can leave off the '-q' option and watch the server come up
    #...then use CTL-C to exit the tty (the container will keep running)
    
    cp systemd/indy-volumes.service systemd/indy.service /etc/systemd/system
    systemctl enable indy-volumes indy
    
    docker stop indy indy-volumes
    systemctl start indy-volumes
    systemctl start indy
    
    # Use this to see the server log as it starts up, to make sure it boots properly.
    journalctl -f

