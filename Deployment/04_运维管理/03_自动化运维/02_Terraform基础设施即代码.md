# Terraform基础设施即代码

> **返回**: [自动化运维首页](README.md) | [运维管理首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [Terraform基础设施即代码](#terraform基础设施即代码)
  - [📋 目录](#-目录)
  - [1. Terraform架构](#1-terraform架构)
  - [2. Provider配置](#2-provider配置)
  - [3. 资源管理](#3-资源管理)
  - [4. 状态管理](#4-状态管理)

---

## 1. Terraform架构

**工作流程**:

```text
1. terraform init    # 初始化
2. terraform plan    # 预览变更
3. terraform apply   # 应用变更
4. terraform destroy # 销毁资源
```

---

## 2. Provider配置

**main.tf**:

```hcl
terraform {
  required_providers {
    vsphere = {
      source  = "hashicorp/vsphere"
      version = "~> 2.5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23.0"
    }
  }
  
  backend "s3" {
    bucket = "terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "vsphere" {
  user           = var.vsphere_user
  password       = var.vsphere_password
  vsphere_server = var.vsphere_server
}
```

---

## 3. 资源管理

**创建VM**:

```hcl
resource "vsphere_virtual_machine" "vm" {
  name             = "web-server"
  resource_pool_id = data.vsphere_compute_cluster.cluster.resource_pool_id
  datastore_id     = data.vsphere_datastore.datastore.id
  
  num_cpus = 4
  memory   = 8192
  guest_id = "ubuntu64Guest"
  
  network_interface {
    network_id = data.vsphere_network.network.id
  }
  
  disk {
    label            = "disk0"
    size             = 50
    thin_provisioned = true
  }
}
```

---

## 4. 状态管理

**远程状态后端**:

```hcl
terraform {
  backend "s3" {
    bucket         = "terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-lock"
  }
}
```

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 完成
