# Easy CDP Installation Guide

-   Tested with: **Cloudera CDP Private Cloud Base 7.1.9 / 7.3.1**

## Introduction

These Ansible playbooks provide a streamlined and automated method for
deploying **Cloudera CDP Private Cloud Base** clusters managed by
**Cloudera Manager (CM)**.

## Requirements

-   Ansible 2.8+
-   RHEL
-   Cloudera CDP Private Cloud Base **7.1.x** or **7.3.x**

## Pre-installation Requirements

### Anti-virus

Anti-virus software **must remain disabled during the entire
installation** to avoid interference with Cloudera Manager agents and
service startup.

### Required Network Ports

  Component          Ports             Description
  ------------------ ----------------- ---------------------------------
  SSH                TCP 22            Automation & administration
  Cloudera Manager   7180 / 7183 TLS   CM Web UI & Agent communication
  Ranger Admin       6080 / 6182 TLS   Ranger Administration UI
  Knox               8443 / 8444 TLS   Gateway Access
  Atlas Server       31000 / 31433     Metadata service
  Hue                8888 / 8889       UI access
  SMM                9991              Streams Messaging Manager

### Services requiring a dedicated database

-   Cloudera Manager Server\
-   Oozie Server\
-   Sqoop Server\
-   Reports Manager\
-   Hive Metastore\
-   Hue\
-   Ranger\
-   Schema Registry\
-   Streams Messaging Manager\
-   Knox\
-   Ranger KMS

## Linux Installation Account

    deploy ALL=(ALL) NOPASSWD:ALL

## Active Directory Requirements

-   Provide a dedicated OU for CDP\
-   Provide an account with **full control** over users, groups, and
    computer objects

## Operating System Requirements

-   RHEL 9.4 / 9.5\
-   SSHD enabled

## Networking Requirements

-   Static IPs\
-   FQDN hostnames (lowercase)\
-   DNS forward & reverse lookup\
-   No multihoming

## Disk Requirements

Use `noatime` for all HDFS disks.

## Cluster Configuration

### Basic Administration

``` yaml
admin_user: admin
admin_password: Secure123!
cloudera_manager_admin_password: "{{ admin_password }}"
```

### Java

``` yaml
java_version: openjdk-17-jdk
```

### Databases

``` yaml
database_type: postgresql
database_password: "{{ admin_password }}"
```

### FreeIPA/Kerberos

``` yaml
freeipa_install: no
freeipa_client_install: no
database_install: no
```

### Repository

``` yaml
repo_host: "{{ groups['httpd_repo'][0] | default('localhost') }}"
httpd_port: 8080
cloudera_archive_base_url: "http://{{ repo_host }}:{{ httpd_port }}/cloudera-repos"
```

## Disk Layout

  Mount        Purpose    Min Size
  ------------ ---------- ----------
  `/`          Root FS    25 GB
  `/var`       Services   100 GB
  `/var/log`   Logs       200 GB
  `/opt`       Parcels    100 GB
  `/tmp`       Temp       20 GB

## HDFS/YARN

``` yaml
datanode_disks:
  - /data/01
  - /data/02
```

## Ozone

``` yaml
ozone_om_disk: /data/ozone/om
ozone_scm_disk: /data/ozone/scm
ozone_recon_disk: /data/ozone/recon
```

## Kafka

``` yaml
kafka_disks:
  - /data/01
  - /data/02
```

## Solr

``` yaml
solr_datadir: /data/solr
infra_solr_datadir: /data/infrasolr
```

## NiFi

``` yaml
nifi_flow_disk: /data/01
nifi_provenance_disks:
  - /data/01
  - /data/02
nifi_content_disks:
  - /data/01
  - /data/02
```

## ZooKeeper

``` yaml
zk_datadir: /data/zk
zk_logdir: /data/zk
```

## Pre-check Commands

    export ANSIBLE_CONFIG=$(pwd)/ansible.cfg
    ansible-playbook ssh_known_hosts.yaml
    ansible -m ping all
    ansible-playbook pre_check.yml

## Installation Workflow

-   deploy_repos.yml\
-   deploy_rbdms.yml\
-   deploy_database.yml\
-   deploy_rbdms_client.yml\
-   setup_prereqs.yml\
-   deploy_scm.yml\
-   deploy_agents.yml\
-   deploy_mgmt.yml\
-   prepare_services.yml\
-   install_cluster.yml

## AutoTLS

Directory structure required under `/tmp/tls/`.

## Kerberos

Multiple deployment options: FreeIPA, AD, or MIT-KDC.

## Proxy Management

``` yaml
state: present
http_proxy: http://proxy.example.com:8080
https_proxy: http://proxy.example.com:8080
no_proxy: localhost
```

## Optional Config

-   SSSD\
-   update_cluster.yml
