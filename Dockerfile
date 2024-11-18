FROM ubuntu:24.04

LABEL authors="Isaac (Ike) Arias <ikester@gmail.com>"

RUN apt-get update && \
	apt-get install -y \
		curl \
		libfreetype6 \
		libglu1-mesa \
		libxi6 \
		libxrender1 \
                libxkbcommon-x11-0 \
                libsm-dev \
                libxxf86vm1 \
		xz-utils && \
	apt-get -y autoremove && \
	rm -rf /var/lib/apt/lists/*

ENV BLENDER_MAJOR 4.2
ENV BLENDER_VERSION 4.2.3
ENV BLENDER_URL https://download.blender.org/release/Blender${BLENDER_MAJOR}/blender-${BLENDER_VERSION}-linux-x64.tar.xz

RUN curl -L ${BLENDER_URL} | tar -xJ -C /usr/local/ && \
	mv /usr/local/blender-${BLENDER_VERSION}-linux-x64 /usr/local/blender

RUN apt-get update && \
        apt-get install -y \
        libgl1 \
                libxfixes3 && \
        apt-get -y autoremove && \
	rm -rf /var/lib/apt/lists/*

ADD     newstage.blend /opt/stage.blend
# CMD         ["--help"]
# ENTRYPOINT  ["blender"]
ENV         LD_LIBRARY_PATH=/usr/local/lib

COPY convert.py /root/convert.py
COPY glb.py /root/glb.py

# VOLUME /media
ENTRYPOINT ["/usr/local/blender/blender", "-b"]