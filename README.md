# Easy to install CDP

-   Tested with: **Cloudera CDP Private Cloud Base 7.1.9 / 7.3.1**



# Introduction
These Ansible playbooks provide a streamlined and automated method for
deploying **Cloudera CDP Private Cloud Base** clusters managed by
**Cloudera Manager (CM)**.

# Requirements
-   Ansible 2.8+
-   RHEL
-   Cloudera CDP Private Cloud Base **7.1.x** or **7.3.x**
 

# Pre-installation Requirements

## Anti-virus
Anti-virus software **must remain disabled during the entire
installation** to avoid interference with Cloudera Manager agents and
service startup.


## Required Network Ports
You need to open some ports

 | Component          | Ports             | Description
  | ------------------ | ----------------- | ---------------------------------|
  | SSH                | TCP 22            | Automation & administration      |
  | Cloudera Manager   | 7180 / 7183 TLS   | CM Web UI & Agent communication. |
  | Ranger Admin       | 6080 / 6182 TLS   | Ranger Administration UI         |
  | Knox               | 8443 / 8444 TLS   | Gateway Access.                  |
  | Atlas Server       | 31000 / 31433     | Metadata service                 |
  | Hue                | 8888 / 8889       | UI access                        |
  | SMM                | 9991              | Streams Messaging Manager        |

###	**Which services need a database for their own metadata?**
	-	Cloudera Manager Server
	-	Oozie Server
	-	Sqoop Server
	-	Reports Manager
	-	Hive Metastore Server
	-	Hue Server
	-	Ranger
	-	Schema Registry
	-	Streams Messaging Manager
  - Knox
  - RangerK%S

## Linux Installation Account
A Linux user with **NOPASSWD sudo** must exist on all nodes:
```
deploy ALL=(ALL) NOPASSWD:ALL
```

## Active Directory Requirements

-   Provide a dedicated OU for CDP
-   Provide an account with **full control** over users, groups, and
    computer objects

## Operating System Requirements

-   RHEL 9.4 / 9.5
-   SSHD enabled

### Requirements
- SSHD enabled  

## Networking Requirements

- Static IPs  
- FQDN hostnames (lowercase)  
- `/etc/hosts` must contain *only* local host entry  
- DNS forward & reverse lookup must work  
- `nscd` enabled for hosts only  
- No multihoming (unless certified)

## Disk Requirements

Use `noatime` for all HDFS disks.


# Cluster Configuration

## Environment Configuration
Initial configuration is performed inside the Ansible inventory and `group_vars`.


## Basic Adminstration
Configuration of administration user
```yaml
admin_user: admin
admin_password: Secure123!
cloudera_manager_admin_password: "{{ admin_password }}"
```

## Java Configuration
```yaml
java_version: openjdk-17-jdk
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
# Directory when you put cloudera license.
entreprise_dir: "{{ inventory_dir }}/../entreprise"
# Private key used by cloudera CM to connect to all hosts
ansible_ssh_private_key_file: "{{ entreprise_dir }}/id_rsa"
# Pathe of cloudera License.
cloudera_manager_license_file: "{{ entreprise_dir }}/license_cloudera.txt"
```


## Local Repository
```yaml
repo_host: "{{ groups['httpd_repo'][0] default('localhost') }}"
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

| Mount      | Purpose                                   | Size         | Notes                                         |          
|------------|-------------------------------------------|--------------|-----------------------------------------------|
| `/`        | Root filesystem                           | ≥ 25 GB      | OS base system                        |                  
| `/home`    | User home directories                     | ≥ 25 GB      |                                             
| `/var`     | System services, packages, spool, etc.    | ≥ 100 GB     | Heavy-write area for many daemons             |     
| `/var/log` | System and application logs               | ≥ 200 GB     | Prevent log growth from filling `/var`        |   
| `/opt`     | Application installs & CDP parcel storage | ≥ 100 GB     | Used by Cloudera parcels                      | 
| `/tmp`     | Temporary storage                         | ≥ 20 GB      | Services & installers use temporary space     | 


# Disk Configuration

## HDFS / YARN

WorkerDisks
- HDFS DataNode dirs + YARN NodeManager local dirs + Impala scratch dirs. Total capacity per node < 100 TB. Do not use disks larger than 8 TB.

```yaml
datanode_disks:
  - /data/01
  - /data/02
```
Master Disks
-  [`namenode_disks `] NameNode disks: In case of multiple disks with JBOD, use /data/nn1, /data/nn2 etc. mount points.
Required only on the 2 Master Nodes that will have the NameNode roles deployed.
-  [`journalnode_disks `] Use dedicated disks to avoid I/O contention.
```yaml
namenode_disks:
  - /data/nn1
  - /data/nn2
journalnode_disks: /data/jn
checkpoint_disks: /data/nn1
```

## Ozone

- [`ozone_om_disk `] – Ozone OM: RAID 1 NVMe required
- [`ozone_scm_disk `] – Disk to Ozone container : RAID 1 NVMe or SSD required.: Storage Container Manager
- [`ozone_recon_disk `] – Disk to Ozone Recon : NVMe (required)
- [`ozone_datanode_storage_disks `] – Ozone data storage: These disks must not be shared with HDFS or another storage system Total capacity per node < 100 TB. Do not use disks larger than 8 TB.
- [`ozone_datanode_disk `] – One or more directories used for storing Ozone metadata. OzoneManager, SCM, and Datanode will write the metadata to this path.

```yaml
ozone_om_disk:    /data/ozone/om
ozone_scm_disk:   /data/ozone/scm
ozone_recon_disk: /data/ozone/recon
ozone_datanode_storage_disks:
  - /data/ozone/dnstorage/data-01
  - /data/ozone/dnstorage/data-02
ozone_datanode_disk: /data/ozone/dn
```


## Kafka
-  full disk, primary partitions, only if you use KAKFA with heavy workloads

```yaml
kafka_disks:
  - /data/01
  - /data/02
```


## Solr

- [`solr_datadir `] – Only if you use Solr Search
- [`infra_solr_datadir`] – CDP-INFRA-SOLR service. Stores collections for Ranger Audits and Atlas.

```yaml
solr_datadir: /data/solr
infra_solr_datadir: /data/infrasolr
```

## NiFi
La liste des disques des NIFI est configurée par la propriété:
- [`nifi_flow_disk `] – Disk for FlowReository 
- [`nifi_provenance_disks`] – Provenance repository 1To + by disks 
- [`nifi_content_disks`] – Content repository 1To + by disks

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
- [`zk_datadir,zk_logdir`] – Use dedicated disks to avoid I/O contention.

```yaml
zk_datadir: /data/zk
zk_logdir: /data/zk
```

# Pre-check Commands

## Preparing Environment Variables
Populate SSH known_hosts on all nodes to avoid interactive SSH prompts. 
```yaml
export ANSIBLE_CONFIG=$(pwd)/ansible.cfg
ansible-playbook ssh_known_hosts.yaml
ansible -m ping all
```

# Installation Workflow

This section describes the ordered execution of Ansible playbooks used to deploy a full CDP Private Cloud Base cluster.


## Preparing the evironnement

1. Create the repository and download cloudera parcels

- `deploy_repos.yml` - Deploys custom OS and Cloudera repositories.

2. Install Postgres and create databases if not created by DBA
- `deploy_rbdms.yml` -  Prepares storage for the database backend (PostgreSQL/MySQL/etc.). 
- `deploy_database.yml` - Installs and configures the database server (PostgreSQL by default). 
- `deploy_rbdms_client.yml` - Installs database client tools needed by CM and services.

3. Applies OS prerequisites
- `pre_check.yml` -  Use ansible scripts pre_check to check prerequisities
- `setup_prereqs.yml` -  Applies OS prerequisites, sysctl, limits, packages, NTP, etc. 
- [x]THP Swapping
- [x] THP Overcommit 
- [x] THP disabled  
- [x] firewalld disabled  
- [x] SELinux disabled or permissive  
- [x] IPv6 disabled  
- [ ] SSHD enabled  
- [x] Passwordless SSH  
- [x] JDK 17 (64-bit) or  JDK 8 (64-bit) or JDK 11 (64-bit)
- [x] Python 3.9 or 3.8 


4. Applies OS prerequisites

## Installation of Cloudera Manager Server and agents
- `deploy_scm.yml` - Installs and configures Cloudera Manager Server (SCM).
- `deploy_agents.yml` - Installs Cloudera Manager Agents on all nodes.
- `deploy_mgmt.yml` - Deploys the Cloudera Management Services cluster.

## Cluster creation

- `prepare_services.yml` - Prepares service configuration before cluster install (templates, configs, etc.).
- `install_cluster.yml` - Install  CDP cluster deployment using API mechanism. 


## AutoTLS  Configuration

1. TLS Preparation

- One certificate per host (FQDN-based)
- One private key per host
- CA certificates:
  - Root CA
  - Intermediate CA
  - Full CA chain
See **TLS Directory Structure** section for placement.


2. TLS Directory Structure

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

3. Host Certificates
Store each host certificate in `/tmp/tls/certs/` and name it using its FQDN:

```
/tmp/tls/certs/<fqdn>.pem
```

4. Private Keys
Store the corresponding private keys in:

```
/tmp/tls/keys/<fqdn>.key
```

5. Certificate Authority Files
Place the CA files in:

```
/tmp/tls/ca/ca.cert.pem
/tmp/tls/ca/intermediate.cert.pem
/tmp/tls/ca/ca-chain.cert.pem
```
6. Apply AUTOTLS

- `deploy_autotls.yml`   Cloudera AutoTLS for automated certificate.


## Kerberos 
### Kerberos Configuration
1. Option[1] - Installation IDM or FreeIPA:  Only if you want to IDM or FreeIPA,
* `deploy_freeipa_server.yml` - Optional:  Installs and configures the FreeIPA identity server. 
* `deploy_freeipa_client.yml` -  Optional: Installs FreeIPA clients on cluster nodes
* `deploy_fix_krb5.yml` -  Applies Kerberos configuration fixes or overrides

2. Option[2] - [AD] Preparation AD
* `deploy_krb5_client.yml` Create and prepare /etc/krb5.conf for AD or MIT-KDC

3. Option[3] - [MIT-KDC] Install and prepare MIT-KDC
TODO
### Enable Kerberos
* `deploy_kerberos.yml` - Deploy Kerberos

## Reinstall every thing
- `cmd_restart_all.yml` -  Restarts CM after TLS or kerberos configurations.


# Proxy Management
- Configuration of http proxy is state is present ==> create http proxy, with absent ==> remove http proxies

```
state: present   # or "absent"

http_proxy: "http://proxy.example.com:8080"
https_proxy: "http://proxy.example.com:8080"
no_proxy: "localhost,127.0.0.1,::1"
enable_yum_proxy: true
```

- `proxy_update.yml` -  Deploy or clean proxy depands of state


# Optional: SSSD Management
- Configuration of sssd 

# Optional: Update configuration of cluster
- This configuration is in `service_config.yml` if you want apply it for some custom, use the script:
