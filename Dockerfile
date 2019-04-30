FROM        ubuntu:18.04

WORKDIR     /tmp/workdir

RUN     apt-get -yqq update && \
        apt-get --no-install-recommends -yqq install blender && \
        rm -rf /var/lib/apt/lists/*

MAINTAINER  Colin McFadden <mcfa0086@umn.edu>

ADD     stage.blend /opt/stage.blend

CMD         ["--help"]
ENTRYPOINT  ["blender"]
ENV         LD_LIBRARY_PATH=/usr/local/lib
