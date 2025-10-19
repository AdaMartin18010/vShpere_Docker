# Ansible自动化

> **返回**: [自动化运维首页](README.md) | [运维管理首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Ansible自动化](#ansible自动化)
  - [📋 目录](#-目录)
  - [1. Ansible架构](#1-ansible架构)
  - [2. Inventory管理](#2-inventory管理)
  - [3. Playbook编写](#3-playbook编写)
  - [4. 最佳实践](#4-最佳实践)

---

## 1. Ansible架构

**工作原理**:

```text
┌──────────────┐
│ Control Node │  (执行ansible命令)
└──────┬───────┘
       │ SSH
       ▼
┌──────────────┐
│ Managed Node │  (被管理服务器)
└──────────────┘
```

---

## 2. Inventory管理

**inventory.ini**:

```ini
[webservers]
web1.example.com
web2.example.com

[databases]
db1.example.com ansible_user=admin

[production:children]
webservers
databases

[production:vars]
ansible_python_interpreter=/usr/bin/python3
```

---

## 3. Playbook编写

**基础Playbook**:

```yaml
---
- name: 部署Web应用
  hosts: webservers
  become: yes
  vars:
    app_version: "1.0.0"
  tasks:
  - name: 安装Nginx
    apt:
      name: nginx
      state: present
      
  - name: 复制配置文件
    template:
      src: nginx.conf.j2
      dest: /etc/nginx/nginx.conf
    notify: restart nginx
      
  - name: 启动Nginx
    service:
      name: nginx
      state: started
      enabled: yes
      
  handlers:
  - name: restart nginx
    service:
      name: nginx
      state: restarted
```

---

## 4. 最佳实践

**目录结构**:

```text
ansible/
├── inventories/
│   ├── production/
│   └── staging/
├── roles/
│   ├── common/
│   ├── nginx/
│   └── app/
├── group_vars/
├── host_vars/
└── playbooks/
```

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 完成
