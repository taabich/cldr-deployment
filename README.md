# 🚀 Automated Deployment of CDP Private Cloud Base

> An Ansible-based solution for deploying and managing **Cloudera CDP Private Cloud Base** clusters, driven by **Cloudera Manager (CM)** API automation.

---

## 📋 Table of Contents

* [1. Overview & Compatibility](#1-overview--compatibility)
* [2. System & Network Prerequisites](#2-system--network-prerequisites)
* [3. Inventory & Configuration Variables](#3-inventory--configuration-variables)
* [4. Disk Configuration and Storage](#4-disk-configuration-and-storage)
* [5. Installation Workflow](#5-installation-workflow)
* [6. Advanced Configuration (TLS, Kerberos, Proxy)](#6-advanced-configuration-tls-kerberos-proxy)
* [7. Running the Playbooks](#7-running-the-playbooks)

---

## 1. Overview & Compatibility

These Ansible playbooks automate the entire cluster deployment lifecycle, including environment setup, CM installation, and final cluster configuration.

* **Tested Compatibility:** **Cloudera CDP Private Cloud Base 7.1.9 / 7.3.1**

---

## 2. System & Network Prerequisites

### 2.1 Software Requirements

| Requirement | Value / Version | Notes |
| :--- | :--- | :--- |
| **Ansible** | 2.8+ | Required on the control node. |
| **Operating System** | RHEL 9.4 / 9.5 | |
| **JDK** | OpenJDK 8, 11, or 17 (64-bit) | JDK 17 is the default variable setting. |
| **Python** | Python 3.8 or 3.9 | Required on all target hosts. |

### 2.2 Host Configuration

| Configuration | Detail |
| :--- | :--- |
| **Linux User** | A user with **NOPASSWD sudo** must exist on all nodes (e.g., `deploy`). |
| **SSH** | SSHD must be enabled. |
| **OS Security** | SELinux disabled or permissive. `firewalld` disabled. |
| **AD Requirements** | Provide a dedicated **OU** for CDP and an account with **full control** over user/group objects. |
| **Anti-Virus** | **Must be disabled** during the entire installation process. |

### 2.3 Network Requirements

* **IPs & Hostnames:** Static IPs and FQDN hostnames (lowercase) are mandatory.
* **Name Resolution:** DNS forward & reverse lookups must function correctly.
* **`/etc/hosts`:** Must contain *only* the local host entry (or follow specific best practices).
* **Multihoming:** No multihoming (multiple NICs on the same subnet) unless certified.
* **`nscd`:** Must be enabled for host lookups only.

### 2.4 Required Network Ports

Ensure the following TCP ports are open:

| Component | Ports | Description |
| :--- | :--- | :--- |
| **SSH** | 22 | Automation & Administration |
| **Cloudera Manager** | 7180 / 7183 (TLS) | CM Web UI & Agent Communication |
| **Ranger Admin** | 6080 / 6182 (TLS) | Ranger Administration UI |
| **Knox** | 8443 / 8444 (TLS) | Gateway Access |
| **Atlas / SMM** | 31000 / 9991 | Metadata service / Streams Messaging Manager |
| **Hue** | 8888 / 8889 | UI access |

### 2.5 Database Dependency

The following services require a dedicated database for their metadata:
* Cloudera Manager Server
* Hive Metastore Server
* Oozie Server
* Ranger, Ranger KMS
* Hue Server, Sqoop Server, Reports Manager
* Knox, Schema Registry, Streams Messaging Manager (SMM)

---

## 3. Inventory & Configuration Variables

Initial configuration is performed within the Ansible inventory and `group_vars`.

### 3.1 Ansible Inventory Structure

The inventory defines host groups by their cluster role using `host_template`.

| Group Name | Purpose | Example Nodes |
| :--- | :--- | :--- |
| `[cloudera_manager]` | **Cloudera Manager (CM)** Server Host | `<CM>` |
| `[cluster_master_nodes]` | **Cluster Masters** (NN, RM, SCM) | `<master1>`, `<master2>`, etc. |
| `[cluster_worker_nodes]` | **Cluster Workers** (DN, NM) | `<worker1>`, `<worker2>`, etc. |
| `[krb5_server]` | **Kerberos KDC** Host (e.g., Active Directory) | `<AD>` |
| `[db_server]` | Dedicated **Cluster Databases** Host | `<db_server>` |
| `[httpd_repo]` | Local **Repository** Server for Parcels/Packages | `<repos_server>` |

### 3.2 Core Variables

| Category | Variable | Description | Default Value |
| :--- | :--- | :--- | :--- |
| **Administration** | `admin_user`, `admin_password` | Default administrative credentials. | `admin`, `Secure123!` |
| **Versions** | `cloudera_manager_version` | CM Version to deploy. | `{{ cldr_versions.cm.version }}` |
| **Database** | `database_type` | Backend database type (e.g., `postgresql`). | `'postgresql'` |
| **IDM** | `freeipa_install` | Toggle FreeIPA server installation. | `no` |

### 3.3 Path & Repository Configuration

These variables define paths to local resources and remote repositories.

```yaml
# --- Enterprise Resources (License & SSH Key) ---
# Directory on the control node containing license and key
entreprise_dir: "{{ inventory_dir }}/../entreprise"
# Private key for CM to connect to hosts
ansible_ssh_private_key_file: "{{ entreprise_dir }}/id_rsa"
cloudera_manager_license_file: "{{ entreprise_dir }}/license_cloudera.txt"

# --- Local Repository Configuration ---
repo_host: "{{ groups['httpd_repo'][0] default('localhost') }}"
httpd_port: 8080
cloudera_archive_base_url: "http://{{ repo_host }}:{{ httpd_port }}/cloudera-repos"
cloudera_manager_repo_url: "{{ cloudera_archive_base_url }}/cm7/{{ cldr_versions.cm.version }}"

```

## 4 Disk Configuration and Storage
### 4.1 General OS Disk Layout (All Nodes)
This layout is essential for separating logs, application binaries, and
system services to ensure stability.


| Mount Point    |   Purpose     |      Minimum Size   |   Notes |
| :--- | :--- | :--- |
|`/var/log`        |System and Application Logs       |≥ 200 GB       |    |  
|`/opt`        |    Application Installs & **CDP  parcels.   Parcel Storage**   |    ≥ 100 GB    |      Used by Cloudera | 
|`/var`        |    System services, packages, spool,for daemons. etc.   ≥ 100 GB    |      Heavy-write area|
|`/`           |      Root filesystem   ≥ 25 GB     |      OS base system.|
|`/tmp`        |    Temporary storage ≥ 20 GB    |       Services and installers use this space. | 
                                                      
                                                     

- **HDFS Disks**    Data disks        Use the       **`noatime`**      mount option.   
                                       
                                       

### 4.2 HDFS / YARN Configuration

#### Worker Disks (`datanode_disks`)

Used for HDFS DataNode, YARN NodeManager local, and Impala scratch
directories.
**Constraint:** Do not use disks larger than **8 TB**. Total capacity
per node **\< 100 TB**.

``` yaml
datanode_disks:
  - /data/01
  - /data/02
```

------------------------------------------------------------------------

### Master Disks (HDFS HA)

  -----------------------------------------------------------------------
  Variable                Service                 Key Requirements
  ----------------------- ----------------------- -----------------------
  `namenode_disks`        NameNode Metadata       Use multiple disks
                                                  (JBOD). Required only
                                                  on NameNode hosts.

  `journalnode_disks`     JournalNode Logs        Dedicated disks
                                                  strongly recommended to
                                                  avoid I/O contention.

  `checkpoint_disks`      Checkpoints             Typically same as
                                                  NameNode disk.
  -----------------------------------------------------------------------

``` yaml
namenode_disks:
  - /data/nn1
  - /data/nn2

journalnode_disks: /data/jn
checkpoint_disks: /data/nn1
```

------------------------------------------------------------------------

### 4.3 Specialized Storage (Ozone, Kafka, NiFi)

  --------------------------------------------------------------------------------
  Service                 Variable(s)                      Key Requirements
  ----------------------- -------------------------------- -----------------------
  ZooKeeper               `zk_datadir`, `zk_logdir`        Dedicated disks
                                                           mandatory to prevent
                                                           I/O contention.

  Kafka                   `kafka_disks`                    Dedicated disks,
                                                           primary partitions (for
                                                           heavy workloads only).

  Solr / Infra-Solr       `solr_datadir`,                  Storage for Solr data
                          `infra_solr_datadir`             (Infra-Solr stores
                                                           Ranger/Atlas audits).

  NiFi                    `nifi_flow_disk`,                Separate disks for
                          `nifi_provenance_disks`,         Flow, Provenance,
                          `nifi_content_disks`             Content (1 TB+
                                                           recommended).

  Ozone OM/SCM            `ozone_om_disk`,                 OM: RAID1 NVMe. SCM:
                          `ozone_scm_disk`                 RAID1 NVMe/SSD.

  Ozone Data              `ozone_datanode_storage_disks`   Must NOT be shared with
                                                           HDFS or other systems.
  --------------------------------------------------------------------------------

------------------------------------------------------------------------

## 5. Installation Workflow

This is the recommended ordered execution of the Ansible playbooks.

### Pre-check Commands

Set Ansible environment:

``` bash
export ANSIBLE_CONFIG=$(pwd)/ansible.cfg
ansible-playbook ssh_known_hosts.yaml
ansible -m ping all
```


------------------------------------------------------------------------

### Step 1: Environment and Database Preparation

#### Repository Setup

-   **deploy_repos.yml** -- Deploy custom OS and Cloudera repositories,
    download parcels.

#### Database Configuration

-   **deploy_rbdms.yml** -- Prepares storage for the DB backend.
-   **deploy_database.yml** -- Installs & configures DB server (if
    `database_install: yes`).
-   **deploy_rbdms_client.yml** -- Installs DB client tools needed by CM
    & services.

#### OS Prerequisites

-   **pre_check.yml** -- Runs pre-check scripts to validate
    prerequisites.
-   **setup_prereqs.yml** -- Applies OS prerequisites (sysctl, limits,
    NTP, disable swap/THP, etc.)

------------------------------------------------------------------------

### Step 2: Cloudera Manager and Agent Installation

-   **deploy_scm.yml** -- Install and configure Cloudera Manager
    Server.
-   **deploy_agents.yml** -- Install Cloudera Manager Agents.
-   **deploy_mgmt.yml** -- Deploy Cloudera Management Services (CMS).

------------------------------------------------------------------------

### Step 3: Cluster Deployment

-   **prepare_services.yml** -- Templates and service configs before
    install.
-   **install_cluster.yml** -- Deploy the CDP cluster using the CM API.

------------------------------------------------------------------------

## 6. Advanced Configuration (TLS, Kerberos, Proxy)

------------------------------------------------------------------------

### 6.1 Kerberos Integration

  ------------------------------------------------------------------------------
  Option                  Context                 Playbooks
  ----------------------- ----------------------- ------------------------------
  IDM / FreeIPA           Full IDM installation   `deploy_freeipa_server.yml`,
                                                  `deploy_freeipa_client.yml`

  Active Directory (AD)   AD integration prep     `deploy_krb5_client.yml`

  MIT-KDC                 MIT KDC deployment      **TODO**
  ------------------------------------------------------------------------------

Final step:\
**deploy_kerberos.yml** -- Enables Kerberos via CM API.

Fixes:\
**deploy_fix_krb5.yml** -- Applies Kerberos overrides.

------------------------------------------------------------------------

### 6.2 AutoTLS Configuration

AutoTLS automates certificate management via CM.

TLS Directory Example:

    /tmp/tls/
      ├── certs/<fqdn>.pem
      ├── keys/<fqdn>.key
      └── ca/ca-chain.cert.pem

``` yaml
tls_workdir_localpath: /tmp/tls
```

Apply AutoTLS:

-   **deploy_autotls.yml**

------------------------------------------------------------------------

### 6.3 Proxy Management (State Driven)

Proxy configuration is controlled by a single variable:

``` yaml
state: present   # or "absent"

http_proxy: "http://proxy.example.com:8080"
https_proxy: "http://proxy.example.com:8080"
no_proxy: "localhost,127.0.0.1,::1"
enable_yum_proxy: true
```

Playbook:\
- **proxy_update.yml**

------------------------------------------------------------------------

### 6.4 Cluster Restart

-   **cmd_restart_all.yml** -- Restarts CM, Agents, and the full cluster
    (post-TLS, post-Kerberos, etc.)

------------------------------------------------------------------------

## 7. Running the Playbooks

### 7.1 Command Structure

``` bash
ansible-playbook -i <INVENTORY_FILE> <PLAYBOOK_NAME.yml>
```
