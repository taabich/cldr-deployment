# ansible-socle-storage

- Tested with: **Cloudera CDP Private Cloud Base 7.1.9 / 7.3.1**

# Table of Contents
- [Introduction](#introduction)
- [Requirements](#requirements)
- [Environment Configuration](#environment-configuration)
- [Cluster Configuration](#cluster-configuration)
- [Database Configuration](#database-configuration)
- [Virtual Mount Configuration](#virtual-mount-configuration)
- [Disk Configuration](#disk-configuration)
- [SmartSense Configuration](#smartsense-configuration)
- [Preparing Environment Variables](#preparing-environment-variables)
- [Cluster Installation](#cluster-installation)
- [SSL Configuration](#ssl-configuration)
- [Kerberos Configuration](#kerberos-configuration)
- [Futures / Roadmap](#futures--roadmap)
- [Cluster Deployment Features](#cluster-deployment-features)
- [Cluster Components](#cluster-components)
- [High Availability Components](#high-availability-components)
- [Security](#security)

# Introduction
These Ansible playbooks provide a method for deploying **Cloudera CDP Private Cloud Base** clusters managed by Ambari.

# Requirements
- Ansible 2.8+
- RHEL
- Cloudera CDP Private Cloud Base

# Environment Configuration
Initial configuration is performed inside the Ansible inventory and `group_vars`.

# Environment Configuration
Initial environment setup is performed in the inventory and `group_vars`.

# Pre-installation Requirements

## Anti-virus
Anti-virus software **must be disabled during the entire installation process** to prevent interference with agent deployment and service startup.

## Required Network Ports

| Component | Ports | Description |
|----------|--------|-------------|
| SSH | TCP 22 | Required for automation and administration |
| Cloudera Manager | 7180 / 7183 (TLS) | CM Web UI + Agent communication |
| Ranger Admin | 6080 / 6182 (TLS) | Ranger UI |
| Knox | 8443 / 8444 (TLS) | Gateway access |
| Atlas Server | 31000 / 31433 (TLS) | Metadata service |
| Hue | 8888 / 8889 | UI access |
| SMM | 9991 | Streams Messaging Manager |


## Linux Installation Account
A Linux user with **NOPASSWD sudo** must exist on all nodes:

```
deploy ALL=(ALL) NOPASSWD:ALL
```

## Active Directory Requirements
If AD integration is required:
- Provide a dedicated OU for CDP.
- Provide an account with **full control** on users, groups, and computer objects inside the OU.
## Operating System Requirements
### OS
- [x] RHEL **9.4**
- [x] RHEL **9.5**

### Requirements
- THP Swapping
  THP Overcommit 
- THP disabled  
- firewalld disabled  
- SELinux disabled or permissive  
- IPv6 disabled  
- SSHD enabled  
- Passwordless SSH  
- JDK 17 (64-bit) or  JDK 8 (64-bit) or JDK 11 (64-bit)
- Python 3.9 or 3.8 

## Networking Requirements

- Static IPs  
- FQDN hostnames (lowercase)  
- `/etc/hosts` must contain *only* local host entry  
- DNS forward & reverse lookup must work  
- `nscd` enabled for hosts only  
- No multihoming (unless certified)

## Disk Requirements
All HDFS disks (NameNode, JournalNode, DataNode) must be mounted with:

```
noatime
```

# Cluster Configuration

## Basic Adminstratuin
```yaml
admin_user: admin
admin_password: Secure123!
cloudera_manager_admin_password: "{{ admin_password }}"
```

## Java Configuration
```yaml
java_version: openjdk-17-jdk
```

## Networking / ECS
```yaml
ecs_enabled: no
```

## Database Backend
```yaml
database_type: 'postgresql'
database_password: "{{ admin_password }}"
```

## Kerberos / FreeIPA
```yaml
freeipa_install: no
freeipa_client_install: no
database_install: no
```

## Enterprise Directory
```yaml
entreprise_dir: "{{ inventory_dir }}/../entreprise"
ansible_ssh_private_key_file: "{{ entreprise_dir }}/id_rsa"
private_key_path: "{{ ansible_ssh_private_key_file }}"
cloudera_manager_license_file: "{{ entreprise_dir }}/license_cloudera.txt"
```

## Cloudera Manager Connection
```yaml
cloudera_manager_host: "{{ groups['cloudera_manager'][0] | default('localhost') }}"
```

## Local Repository
```yaml
repo_host: "{{ groups['httpd_repo'][0] | default('localhost') }}"
httpd_port: 8080
cloudera_archive_base_url: "http://{{ repo_host }}:{{ httpd_port }}/cloudera-repos"
```

## CDP & CM Versions
```yaml
cloudera_runtime_version: "{{ cldr_versions.cdh.version }}"
cloudera_manager_version: "{{ cldr_versions.cm.version }}"
cloudera_manager_repo_url: "{{ cloudera_archive_base_url }}/cm7/{{ cldr_versions.cm.version }}"
```

## Services Auto-Discovery
```yaml
enable_cfm: false
enable_csa: false
enable_spark3: false
```

# Database Configuration

```yaml
postgres_version: The os version
postgresql_data_dir: /data/rbdms
```

# OS Disk Layout (All Nodes)

| Mount      | Purpose                                  | Size         | Notes                                         |
|------------|-------------------------------------------|--------------|-----------------------------------------------|
| `/`        | Root filesystem                           | ≥ 25 GB      | OS base system                                |
| `/home`    | User home directories                     | ≥ 25 GB      |                                               |
| `/var`     | System services, packages, spool, etc.    | ≥ 100 GB     | Heavy-write area for many daemons             |
| `/var/log` | System and application logs               | ≥ 200 GB     | Prevent log growth from filling `/var`        |
| `/opt`     | Application installs & CDP parcel storage | ≥ 100 GB     | Used by Cloudera parcels                      |
| `/tmp`     | Temporary storage                         | ≥ 20 GB      | Services & installers use temporary space     |


# Disk Configuration

## HDFS / YARN

```yaml
datanode_disks:
  - /data/01
  - /data/02
namenode_disks:
  - /data/nn1
journalnode_disks: /data/jn
checkpoint_disks: /data/nn1
```

## Kafka
```yaml
kafka_disks:
  - /data/01
  - /data/02
```

## Ozone
```yaml
ozone_om_disk:    /data/ozone/om
ozone_scm_disk:   /data/ozone/scm
ozone_recon_disk: /data/ozone/recon
ozone_datanode_storage_disks:
  - /data/ozone/dnstorage/data-01
  - /data/ozone/dnstorage/data-02
ozone_datanode_disk: /data/ozone/dn
```

## Solr
```yaml
solr_datadir: /data/solr
infra_solr_datadir: /data/infrasolr
```

## NiFi
```yaml
nifi_flow_disk: /data/01
nifi_provenance_disks:
  - /data/01
  - /data/02
nifi_content_disks:
  - /data/01
  - /data/02
```

## ZooKeeper
```yaml
zk_datadir: /data/zk
zk_logdir: /data/zk
```



# Preparing Environment Variables

```
export ANSIBLE_CONFIG=$(pwd)/ansible.cfg
ansible-playbook ssh_known_hosts.yaml
ansible -m ping all
```


# Cluster Installation
## Playbook Execution Order and Description


## Playbook Execution Order and Description

This section describes the ordered execution of Ansible playbooks used to deploy a full CDP Private Cloud Base cluster.

| Playbook | Enabled | Purpose |
|----------|---------|----------|
| `ssh_known_hosts.yml` |  Populate SSH known_hosts on all nodes to avoid interactive SSH prompts. |
| `deploy_freeipa_server.yml` | Installs and configures the FreeIPA identity server. |
| `deploy_freeipa_client.yml` |  Installs FreeIPA clients on cluster nodes. |
| `deploy_fix_krb5.yml` |  Applies Kerberos configuration fixes or overrides. |
| `deploy_repos.yml` |  Deploys custom OS and Cloudera repositories. |
| `deploy_rbdms.yml` | Conditional (`when: database_install`) | Prepares storage for the database backend (PostgreSQL/MySQL/etc.). |
| `deploy_database.yml` | Conditional (`when: database_install`) | Installs and configures the database server (PostgreSQL by default). |
| `deploy_rbdms_client.yml` | Installs database client tools needed by CM and services. |
| `setup_prereqs.yml` |  Applies OS prerequisites, sysctl, limits, packages, NTP, etc. |
| `deploy_scm.yml` |  Installs and configures Cloudera Manager Server (SCM). |
| `deploy_agents.yml` | Installs Cloudera Manager Agents on all nodes. |
| `deploy_mgmt.yml` |  Deploys the Cloudera Management Services cluster. |
| `cmd_restart_scm.yml` |  Restarts Cloudera Manager Server. |
| `cmd_restart_agents.yml` |  Restarts Cloudera Manager Agents. |
| `prepare_services.yml` | Prepares service configuration before cluster install (templates, configs, etc.). |
| `install_cluster.yml` |  Install  CDP cluster deployment using API mechanism. |
| `cmd_scm_restart.yml` |  Restarts CM after TLS or repo operations. |
| `cmd_agents_restart.yml` |  Forces agent restart (useful after TLS/certs). |

# AutoTLS  Configuration

## TLS Preparation

- One certificate per host (FQDN-based)
- One private key per host
- CA certificates:
  - Root CA
  - Intermediate CA
  - Full CA chain
See **TLS Directory Structure** section for placement.


## TLS Directory Structure

Configure TLS work directory
```yaml
tls_workdir_localpath: /tmp/tls
```

Before enabling TLS or AutoTLS, prepare the following directory structure under `/tmp/tls`:



```
/tmp/tls/
├── certs/
├── keys/
└── ca/
```

## Host Certificates
Store each host certificate in `/tmp/tls/certs/` and name it using its FQDN:

```
/tmp/tls/certs/<fqdn>.pem
```

## Private Keys
Store the corresponding private keys in:

```
/tmp/tls/keys/<fqdn>.key
```

## Certificate Authority Files
Place the CA files in:

```
/tmp/tls/ca/ca.cert.pem
/tmp/tls/ca/intermediate.cert.pem
/tmp/tls/ca/ca-chain.cert.pem
```
## Apply AUTOTLS
| Playbook | Enabled | Purpose |
|----------|---------|----------|
| `deploy_autotls.yml` |  Enables Cloudera AutoTLS for automated certificate provisioning. |


# Kerberos Configuration
(To be completed.)


# Cluster Deployment Features
- External DB support
- Cloudera Manager Server
- Cloudera Manager Agent
- Cloudera CMS
- CDP Runtime deployment

# Cluster Components

### CDP Services
HDFS, YARN, Hive, HBase, Oozie, ZooKeeper, Atlas, Kafka, Knox, Ranger, Ranger KMS...



