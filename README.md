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