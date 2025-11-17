FROM rockylinux:9
LABEL maintainer="MTA"

ARG USERNAME
ARG USER_UID
ARG USER_GID

# Systemd-friendly environment
ENV container=docker

# Base tools (Rocky 9 uses python3/pip3)
RUN dnf -y update && \
    dnf -y install \
      systemd \
      git \
      python3 \
      python3-pip \
      sudo \
      openssh-server \
      openssh-clients \
      unzip \
      tar \
      rsync \
      fuse-libs && \
    dnf clean all

# Install Ansible
RUN python3 -m pip install --upgrade pip && \
    python3 -m pip install ansible-core ansible jmespath && \
    ln -sf /usr/local/bin/ansible* /usr/bin/ || true

# Disable requiretty for sudo
RUN sed -i -e 's/^\(Defaults\s*requiretty\)/#--- \1/' /etc/sudoers

# Minimal Ansible localhost inventory
RUN mkdir -p /etc/ansible && \
    printf '[local]\nlocalhost ansible_connection=local\n' > /etc/ansible/hosts

# --- Create dynamic user/group (handle existing UID/GID gracefully) ---
RUN set -eux; \
    if getent group "${USER_GID}" >/dev/null; then \
      gname="$(getent group ${USER_GID} | cut -d: -f1)"; \
      if [ "${gname}" != "${USERNAME}" ]; then groupmod -n "${USERNAME}" "${gname}"; fi; \
    else \
      groupadd -g "${USER_GID}" "${USERNAME}"; \
    fi; \
    if getent passwd "${USER_UID}" >/dev/null; then \
      useradd -m -s /bin/bash -g "${USER_GID}" "${USERNAME}"; \
    else \
      useradd -m -s /bin/bash -u "${USER_UID}" -g "${USER_GID}" "${USERNAME}"; \
    fi; \
    echo "%${USERNAME} ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Prepare SSH directory (keys optional – add later if you want)
USER ${USERNAME}
WORKDIR /home/${USERNAME}
RUN mkdir -p /home/${USERNAME}/.ssh && chmod 700 /home/${USERNAME}/.ssh

# Final settings for systemd-in-container
USER root
VOLUME ["/sys/fs/cgroup"]
STOPSIGNAL SIGRTMIN+3
CMD ["/usr/sbin/init"]