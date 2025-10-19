# 05 - CSI驱动详解

**作者**: 云原生存储专家团队  
**创建日期**: 2025-10-19  
**最后更新**: 2025-10-19  
**版本**: v1.0

---

## 📋 本章导航

- [05 - CSI驱动详解](#05---csi驱动详解)
  - [📋 本章导航](#-本章导航)
  - [1. CSI架构与规范](#1-csi架构与规范)
    - [1.1 CSI概述](#11-csi概述)
    - [1.2 CSI规范](#12-csi规范)
    - [1.3 CSI架构](#13-csi架构)
    - [1.4 Kubernetes CSI集成](#14-kubernetes-csi集成)
  - [2. CSI插件开发](#2-csi插件开发)
    - [2.1 开发环境准备](#21-开发环境准备)
    - [2.2 Identity Service](#22-identity-service)
    - [2.3 Controller Service](#23-controller-service)
    - [2.4 Node Service](#24-node-service)
  - [3. 常用CSI驱动](#3-常用csi驱动)
    - [3.1 Rook CSI for Ceph](#31-rook-csi-for-ceph)
    - [3.2 CSI for NFS](#32-csi-for-nfs)
    - [3.3 CSI HostPath](#33-csi-hostpath)
    - [3.4 云厂商CSI](#34-云厂商csi)
  - [4. CSI高级特性](#4-csi高级特性)
    - [4.1 Volume Snapshot](#41-volume-snapshot)
    - [4.2 Volume Clone](#42-volume-clone)
    - [4.3 Volume Resize](#43-volume-resize)
    - [4.4 Topology感知](#44-topology感知)
  - [5. 最佳实践](#5-最佳实践)
    - [5.1 性能优化](#51-性能优化)
    - [5.2 安全加固](#52-安全加固)
    - [5.3 故障排查](#53-故障排查)
  - [6. 总结](#6-总结)

---

## 1. CSI架构与规范

### 1.1 CSI概述

**CSI (Container Storage Interface)** 是CNCF定义的容器存储接口标准，用于在Kubernetes等容器编排系统中实现可插拔的存储驱动。

```yaml
CSI优势:
  ✅ 标准化接口 (跨平台)
  ✅ 解耦存储与编排系统
  ✅ 插件式架构
  ✅ 厂商中立
  ✅ 易于维护和升级
  ✅ 丰富的生态系统

CSI发展历程:
  2017: CSI 0.1 (Alpha)
  2018: CSI 1.0 (GA)
  2019: CSI 1.1 (快照、克隆)
  2020: CSI 1.2 (拓扑感知)
  2021: CSI 1.3 (健康检查)
  2022: CSI 1.4-1.6 (增强特性)
  2023: CSI 1.7 (卷组)
  2024: CSI 1.8 (性能优化)
  2025: CSI 1.9+ (未来特性)

支持的编排系统:
  ✅ Kubernetes 1.13+
  ✅ OpenShift 4.x
  ✅ Rancher 2.x
  ✅ Nomad 0.9+
  ✅ Mesos
```

---

### 1.2 CSI规范

**CSI Spec 1.8.0** (2024-2025):

```yaml
CSI规范结构:
  
1. Identity Service (身份服务):
   功能:
     - 获取插件信息
     - 获取插件能力
     - 健康检查
   
   RPC:
     - GetPluginInfo
     - GetPluginCapabilities
     - Probe

2. Controller Service (控制器服务):
   功能:
     - 创建/删除卷
     - 发布/取消发布卷
     - 快照/克隆
     - 扩容
   
   RPC:
     - CreateVolume
     - DeleteVolume
     - ControllerPublishVolume
     - ControllerUnpublishVolume
     - ValidateVolumeCapabilities
     - ListVolumes
     - GetCapacity
     - CreateSnapshot
     - DeleteSnapshot
     - ControllerExpandVolume

3. Node Service (节点服务):
   功能:
     - 挂载卷到节点
     - 卸载卷
     - 节点信息报告
   
   RPC:
     - NodeStageVolume
     - NodeUnstageVolume
     - NodePublishVolume
     - NodeUnpublishVolume
     - NodeGetVolumeStats
     - NodeExpandVolume
     - NodeGetCapabilities
     - NodeGetInfo

CSI能力 (Capabilities):
  Controller:
    - CREATE_DELETE_VOLUME
    - PUBLISH_UNPUBLISH_VOLUME
    - LIST_VOLUMES
    - GET_CAPACITY
    - CREATE_DELETE_SNAPSHOT
    - CLONE_VOLUME
    - EXPAND_VOLUME
    - VOLUME_CONDITION
  
  Volume:
    - STAGE_UNSTAGE_VOLUME
    - EXPAND_VOLUME
    - VOLUME_CONDITION
    - VOLUME_MOUNT_GROUP
  
  Node:
    - STAGE_UNSTAGE_VOLUME
    - GET_VOLUME_STATS
    - EXPAND_VOLUME
    - VOLUME_CONDITION
```

---

### 1.3 CSI架构

**CSI插件架构图**:

```text
CSI架构:

┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                       │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              Kubernetes API Server                     │ │
│  └─────────┬──────────────────────────┬───────────────────┘ │
│            │                          │                     │
│            │                          │                     │
│  ┌─────────▼──────────────┐  ┌────────▼──────────────────┐ │
│  │  PersistentVolumeClaim │  │  VolumeAttachment (CRD)   │ │
│  │  (PVC)                 │  │  - CSI插件绑定            │ │
│  └─────────┬──────────────┘  └────────┬──────────────────┘ │
│            │                          │                     │
│            │                          │                     │
│  ┌─────────▼──────────────────────────▼───────────────────┐ │
│  │           Kubernetes Control Plane                     │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │       external-provisioner (Sidecar)             │  │ │
│  │  │  - Watch PVC                                     │  │ │
│  │  │  - Call CreateVolume                             │  │ │
│  │  │  - Create PV                                     │  │ │
│  │  └────────────────────┬─────────────────────────────┘  │ │
│  │                       │                                 │ │
│  │  ┌────────────────────▼─────────────────────────────┐  │ │
│  │  │       external-attacher (Sidecar)                │  │ │
│  │  │  - Watch VolumeAttachment                        │  │ │
│  │  │  - Call ControllerPublishVolume                  │  │ │
│  │  └────────────────────┬─────────────────────────────┘  │ │
│  │                       │                                 │ │
│  │  ┌────────────────────▼─────────────────────────────┐  │ │
│  │  │       external-resizer (Sidecar)                 │  │ │
│  │  │  - Watch PVC resize                              │  │ │
│  │  │  - Call ControllerExpandVolume                   │  │ │
│  │  └────────────────────┬─────────────────────────────┘  │ │
│  │                       │                                 │ │
│  │  ┌────────────────────▼─────────────────────────────┐  │ │
│  │  │       external-snapshotter (Sidecar)             │  │ │
│  │  │  - Watch VolumeSnapshot                          │  │ │
│  │  │  - Call CreateSnapshot                           │  │ │
│  │  └────────────────────┬─────────────────────────────┘  │ │
│  │                       │                                 │ │
│  │  ┌────────────────────▼─────────────────────────────┐  │ │
│  │  │      CSI Driver (Controller Plugin)              │  │ │
│  │  │  - Identity Service                              │  │ │
│  │  │  - Controller Service                            │  │ │
│  │  │  - gRPC Server (Unix Socket)                     │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌────────────────────────────────────────────────────────┐ │
│  │           Kubernetes Worker Nodes                      │ │
│  │                                                         │ │
│  │  ┌──────────────────────────────────────────────────┐  │ │
│  │  │       kubelet (每个节点)                          │  │ │
│  │  │  - Volume Manager                                │  │ │
│  │  │  - Call NodeStageVolume                          │  │ │
│  │  │  - Call NodePublishVolume                        │  │ │
│  │  └────────────────────┬─────────────────────────────┘  │ │
│  │                       │                                 │ │
│  │  ┌────────────────────▼─────────────────────────────┐  │ │
│  │  │      CSI Driver (Node Plugin)                    │  │ │
│  │  │  - Node Service                                  │  │ │
│  │  │  - gRPC Server (Unix Socket)                     │  │ │
│  │  │  - DaemonSet (每个节点)                          │  │ │
│  │  └──────────────────────────────────────────────────┘  │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────┬───────────────────────────┘
                                  │
                      ┌───────────▼───────────┐
                      │   Storage Backend     │
                      │   (Ceph/NFS/云存储)   │
                      └───────────────────────┘
```

**组件说明**:

```yaml
1. external-provisioner:
   功能:
     - 监听PVC创建/删除
     - 调用CSI CreateVolume/DeleteVolume
     - 创建/删除PV对象
   
   部署:
     - Sidecar容器
     - 与CSI Controller Plugin同Pod

2. external-attacher:
   功能:
     - 监听VolumeAttachment CRD
     - 调用CSI ControllerPublishVolume/ControllerUnpublishVolume
     - 更新VolumeAttachment状态
   
   部署:
     - Sidecar容器
     - 与CSI Controller Plugin同Pod

3. external-resizer:
   功能:
     - 监听PVC扩容请求
     - 调用CSI ControllerExpandVolume
     - 更新PVC/PV状态
   
   部署:
     - Sidecar容器 (可选)
     - 支持在线扩容

4. external-snapshotter:
   功能:
     - 监听VolumeSnapshot CRD
     - 调用CSI CreateSnapshot/DeleteSnapshot
     - 管理VolumeSnapshotContent
   
   部署:
     - Sidecar容器 (可选)
     - 支持快照功能

5. CSI Driver (Controller Plugin):
   功能:
     - Identity Service (插件信息)
     - Controller Service (卷管理)
     - gRPC Server (Unix Socket)
   
   部署:
     - Deployment/StatefulSet
     - 1-3个副本 (高可用)
     - 运行在控制平面

6. CSI Driver (Node Plugin):
   功能:
     - Identity Service (插件信息)
     - Node Service (节点卷操作)
     - 挂载/卸载卷
   
   部署:
     - DaemonSet (每个节点)
     - Privileged模式
     - 访问宿主机文件系统

7. kubelet:
   功能:
     - Volume Manager
     - 调用CSI Node Service
     - 管理Pod卷生命周期
   
   通信:
     - Unix Socket (/var/lib/kubelet/plugins/...)
     - gRPC
```

---

### 1.4 Kubernetes CSI集成

**CSI CRD (Custom Resource Definitions)**:

```yaml
# 1. CSIDriver CRD
apiVersion: storage.k8s.io/v1
kind: CSIDriver
metadata:
  name: rook-ceph.rbd.csi.ceph.com
spec:
  # 是否需要附加
  attachRequired: true
  
  # Pod信息
  podInfoOnMount: false
  
  # Volume生命周期模式
  volumeLifecycleModes:
  - Persistent
  - Ephemeral
  
  # 存储容量跟踪
  storageCapacity: true
  
  # 支持的FSGroup策略
  fsGroupPolicy: File

---
# 2. CSINode CRD (自动创建)
apiVersion: storage.k8s.io/v1
kind: CSINode
metadata:
  name: node1
spec:
  drivers:
  - name: rook-ceph.rbd.csi.ceph.com
    nodeID: node1
    topologyKeys:
    - topology.kubernetes.io/region
    - topology.kubernetes.io/zone
    allocatable:
      count: 100  # 最大可挂载卷数

---
# 3. VolumeAttachment CRD (自动创建)
apiVersion: storage.k8s.io/v1
kind: VolumeAttachment
metadata:
  name: csi-xxxx
spec:
  attacher: rook-ceph.rbd.csi.ceph.com
  nodeName: node1
  source:
    persistentVolumeName: pvc-xxxx

---
# 4. VolumeSnapshot CRD
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: my-snapshot
  namespace: default
spec:
  volumeSnapshotClassName: csi-ceph-rbd-snapclass
  source:
    persistentVolumeClaimName: my-pvc

---
# 5. VolumeSnapshotClass CRD
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-ceph-rbd-snapclass
driver: rook-ceph.rbd.csi.ceph.com
deletionPolicy: Delete
parameters:
  clusterID: rook-ceph
  csi.storage.k8s.io/snapshotter-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/snapshotter-secret-namespace: rook-ceph
```

---

## 2. CSI插件开发

### 2.1 开发环境准备

**依赖工具**:

```bash
# 1. 安装Go (1.20+)
wget https://go.dev/dl/go1.21.0.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.21.0.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin

# 2. 安装Protobuf编译器
sudo apt-get install -y protobuf-compiler

# 3. 安装Go protobuf插件
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# 4. 克隆CSI规范
git clone https://github.com/container-storage-interface/spec.git

# 5. 初始化项目
mkdir my-csi-driver
cd my-csi-driver
go mod init github.com/myorg/my-csi-driver

# 6. 安装CSI依赖
go get github.com/container-storage-interface/spec/lib/go/csi
go get google.golang.org/grpc
go get github.com/kubernetes-csi/csi-lib-utils/connection
go get github.com/kubernetes-csi/csi-lib-utils/rpc
```

**项目结构**:

```text
my-csi-driver/
├── cmd/
│   └── driver/
│       └── main.go          # 主入口
├── pkg/
│   ├── driver/
│   │   ├── driver.go        # Driver主逻辑
│   │   ├── identity.go      # Identity Service
│   │   ├── controller.go    # Controller Service
│   │   └── node.go          # Node Service
│   └── backend/
│       └── storage.go       # 存储后端接口
├── deploy/
│   ├── kubernetes/
│   │   ├── controller.yaml  # Controller Plugin部署
│   │   ├── node.yaml        # Node Plugin部署
│   │   └── rbac.yaml        # RBAC权限
│   └── helm/
│       └── chart/           # Helm Chart
├── go.mod
├── go.sum
├── Dockerfile
├── Makefile
└── README.md
```

---

### 2.2 Identity Service

**`pkg/driver/identity.go`**:

```go
package driver

import (
 "context"
 "github.com/container-storage-interface/spec/lib/go/csi"
 "google.golang.org/grpc/codes"
 "google.golang.org/grpc/status"
)

// IdentityServer实现CSI Identity Service
type IdentityServer struct {
 driver *Driver
}

// GetPluginInfo返回插件信息
func (ids *IdentityServer) GetPluginInfo(
 ctx context.Context,
 req *csi.GetPluginInfoRequest,
) (*csi.GetPluginInfoResponse, error) {
 if ids.driver.name == "" {
  return nil, status.Error(codes.Unavailable, "Driver name not configured")
 }

 if ids.driver.version == "" {
  return nil, status.Error(codes.Unavailable, "Driver version not configured")
 }

 return &csi.GetPluginInfoResponse{
  Name:          ids.driver.name,
  VendorVersion: ids.driver.version,
 }, nil
}

// GetPluginCapabilities返回插件能力
func (ids *IdentityServer) GetPluginCapabilities(
 ctx context.Context,
 req *csi.GetPluginCapabilitiesRequest,
) (*csi.GetPluginCapabilitiesResponse, error) {
 return &csi.GetPluginCapabilitiesResponse{
  Capabilities: []*csi.PluginCapability{
   {
    Type: &csi.PluginCapability_Service_{
     Service: &csi.PluginCapability_Service{
      Type: csi.PluginCapability_Service_CONTROLLER_SERVICE,
     },
    },
   },
   {
    Type: &csi.PluginCapability_Service_{
     Service: &csi.PluginCapability_Service{
      Type: csi.PluginCapability_Service_VOLUME_ACCESSIBILITY_CONSTRAINTS,
     },
    },
   },
   {
    Type: &csi.PluginCapability_VolumeExpansion_{
     VolumeExpansion: &csi.PluginCapability_VolumeExpansion{
      Type: csi.PluginCapability_VolumeExpansion_ONLINE,
     },
    },
   },
  },
 }, nil
}

// Probe健康检查
func (ids *IdentityServer) Probe(
 ctx context.Context,
 req *csi.ProbeRequest,
) (*csi.ProbeResponse, error) {
 return &csi.ProbeResponse{
  Ready: &wrappers.BoolValue{Value: true},
 }, nil
}
```

---

### 2.3 Controller Service

**`pkg/driver/controller.go`**:

```go
package driver

import (
 "context"
 "fmt"
 "github.com/container-storage-interface/spec/lib/go/csi"
 "google.golang.org/grpc/codes"
 "google.golang.org/grpc/status"
 "strconv"
)

// ControllerServer实现CSI Controller Service
type ControllerServer struct {
 driver *Driver
}

// CreateVolume创建卷
func (cs *ControllerServer) CreateVolume(
 ctx context.Context,
 req *csi.CreateVolumeRequest,
) (*csi.CreateVolumeResponse, error) {
 // 1. 验证参数
 if req.GetName() == "" {
  return nil, status.Error(codes.InvalidArgument, "Volume name missing in request")
 }

 caps := req.GetVolumeCapabilities()
 if caps == nil {
  return nil, status.Error(codes.InvalidArgument, "Volume capabilities missing in request")
 }

 // 2. 检查卷是否已存在
 volumeID := req.GetName()
 if cs.driver.volumes[volumeID] != nil {
  // 已存在，返回幂等响应
  return &csi.CreateVolumeResponse{
   Volume: cs.driver.volumes[volumeID],
  }, nil
 }

 // 3. 解析容量
 requiredBytes := req.GetCapacityRange().GetRequiredBytes()
 if requiredBytes == 0 {
  requiredBytes = 1 * 1024 * 1024 * 1024 // 默认1GiB
 }

 // 4. 创建卷 (调用存储后端)
 err := cs.driver.backend.CreateVolume(volumeID, requiredBytes, req.GetParameters())
 if err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to create volume: %v", err)
 }

 // 5. 构造响应
 volume := &csi.Volume{
  VolumeId:      volumeID,
  CapacityBytes: requiredBytes,
  VolumeContext: req.GetParameters(),
 }

 // 6. 拓扑感知 (可选)
 if req.GetAccessibilityRequirements() != nil {
  volume.AccessibleTopology = []*csi.Topology{
   {
    Segments: map[string]string{
     "topology.kubernetes.io/region": "us-east-1",
     "topology.kubernetes.io/zone":   "us-east-1a",
    },
   },
  }
 }

 // 7. 缓存卷信息
 cs.driver.volumes[volumeID] = volume

 return &csi.CreateVolumeResponse{
  Volume: volume,
 }, nil
}

// DeleteVolume删除卷
func (cs *ControllerServer) DeleteVolume(
 ctx context.Context,
 req *csi.DeleteVolumeRequest,
) (*csi.DeleteVolumeResponse, error) {
 // 1. 验证参数
 volumeID := req.GetVolumeId()
 if volumeID == "" {
  return nil, status.Error(codes.InvalidArgument, "Volume ID missing in request")
 }

 // 2. 检查卷是否存在
 if cs.driver.volumes[volumeID] == nil {
  // 不存在，返回幂等响应
  return &csi.DeleteVolumeResponse{}, nil
 }

 // 3. 删除卷 (调用存储后端)
 err := cs.driver.backend.DeleteVolume(volumeID)
 if err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to delete volume: %v", err)
 }

 // 4. 从缓存中删除
 delete(cs.driver.volumes, volumeID)

 return &csi.DeleteVolumeResponse{}, nil
}

// ControllerPublishVolume附加卷到节点
func (cs *ControllerServer) ControllerPublishVolume(
 ctx context.Context,
 req *csi.ControllerPublishVolumeRequest,
) (*csi.ControllerPublishVolumeResponse, error) {
 volumeID := req.GetVolumeId()
 nodeID := req.GetNodeId()

 // 附加卷到节点 (存储后端实现)
 err := cs.driver.backend.AttachVolume(volumeID, nodeID)
 if err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to attach volume: %v", err)
 }

 return &csi.ControllerPublishVolumeResponse{
  PublishContext: map[string]string{
   "devicePath": fmt.Sprintf("/dev/disk/by-id/%s", volumeID),
  },
 }, nil
}

// ControllerUnpublishVolume从节点分离卷
func (cs *ControllerServer) ControllerUnpublishVolume(
 ctx context.Context,
 req *csi.ControllerUnpublishVolumeRequest,
) (*csi.ControllerUnpublishVolumeResponse, error) {
 volumeID := req.GetVolumeId()
 nodeID := req.GetNodeId()

 // 分离卷 (存储后端实现)
 err := cs.driver.backend.DetachVolume(volumeID, nodeID)
 if err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to detach volume: %v", err)
 }

 return &csi.ControllerUnpublishVolumeResponse{}, nil
}

// ValidateVolumeCapabilities验证卷能力
func (cs *ControllerServer) ValidateVolumeCapabilities(
 ctx context.Context,
 req *csi.ValidateVolumeCapabilitiesRequest,
) (*csi.ValidateVolumeCapabilitiesResponse, error) {
 volumeID := req.GetVolumeId()
 if volumeID == "" {
  return nil, status.Error(codes.InvalidArgument, "Volume ID missing in request")
 }

 caps := req.GetVolumeCapabilities()
 if caps == nil {
  return nil, status.Error(codes.InvalidArgument, "Volume capabilities missing in request")
 }

 // 验证能力
 for _, cap := range caps {
  if cap.GetBlock() != nil {
   // 支持块设备
  } else if cap.GetMount() != nil {
   // 支持文件系统
  }
 }

 return &csi.ValidateVolumeCapabilitiesResponse{
  Confirmed: &csi.ValidateVolumeCapabilitiesResponse_Confirmed{
   VolumeContext:      req.GetVolumeContext(),
   VolumeCapabilities: req.GetVolumeCapabilities(),
  },
 }, nil
}

// ControllerExpandVolume扩容卷
func (cs *ControllerServer) ControllerExpandVolume(
 ctx context.Context,
 req *csi.ControllerExpandVolumeRequest,
) (*csi.ControllerExpandVolumeResponse, error) {
 volumeID := req.GetVolumeId()
 requiredBytes := req.GetCapacityRange().GetRequiredBytes()

 // 扩容卷 (存储后端实现)
 err := cs.driver.backend.ExpandVolume(volumeID, requiredBytes)
 if err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to expand volume: %v", err)
 }

 return &csi.ControllerExpandVolumeResponse{
  CapacityBytes:         requiredBytes,
  NodeExpansionRequired: true, // 需要节点扩容
 }, nil
}

// CreateSnapshot创建快照
func (cs *ControllerServer) CreateSnapshot(
 ctx context.Context,
 req *csi.CreateSnapshotRequest,
) (*csi.CreateSnapshotResponse, error) {
 sourceVolumeID := req.GetSourceVolumeId()
 snapshotName := req.GetName()

 // 创建快照 (存储后端实现)
 snapshotID, err := cs.driver.backend.CreateSnapshot(sourceVolumeID, snapshotName)
 if err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to create snapshot: %v", err)
 }

 snapshot := &csi.Snapshot{
  SnapshotId:     snapshotID,
  SourceVolumeId: sourceVolumeID,
  CreationTime:   ptypes.TimestampNow(),
  ReadyToUse:     true,
 }

 return &csi.CreateSnapshotResponse{
  Snapshot: snapshot,
 }, nil
}

// ControllerGetCapabilities返回Controller能力
func (cs *ControllerServer) ControllerGetCapabilities(
 ctx context.Context,
 req *csi.ControllerGetCapabilitiesRequest,
) (*csi.ControllerGetCapabilitiesResponse, error) {
 return &csi.ControllerGetCapabilitiesResponse{
  Capabilities: []*csi.ControllerServiceCapability{
   {
    Type: &csi.ControllerServiceCapability_Rpc{
     Rpc: &csi.ControllerServiceCapability_RPC{
      Type: csi.ControllerServiceCapability_RPC_CREATE_DELETE_VOLUME,
     },
    },
   },
   {
    Type: &csi.ControllerServiceCapability_Rpc{
     Rpc: &csi.ControllerServiceCapability_RPC{
      Type: csi.ControllerServiceCapability_RPC_PUBLISH_UNPUBLISH_VOLUME,
     },
    },
   },
   {
    Type: &csi.ControllerServiceCapability_Rpc{
     Rpc: &csi.ControllerServiceCapability_RPC{
      Type: csi.ControllerServiceCapability_RPC_CREATE_DELETE_SNAPSHOT,
     },
    },
   },
   {
    Type: &csi.ControllerServiceCapability_Rpc{
     Rpc: &csi.ControllerServiceCapability_RPC{
      Type: csi.ControllerServiceCapability_RPC_CLONE_VOLUME,
     },
    },
   },
   {
    Type: &csi.ControllerServiceCapability_Rpc{
     Rpc: &csi.ControllerServiceCapability_RPC{
      Type: csi.ControllerServiceCapability_RPC_EXPAND_VOLUME,
     },
    },
   },
  },
 }, nil
}
```

---

### 2.4 Node Service

**`pkg/driver/node.go`**:

```go
package driver

import (
 "context"
 "fmt"
 "github.com/container-storage-interface/spec/lib/go/csi"
 "google.golang.org/grpc/codes"
 "google.golang.org/grpc/status"
 "os"
 "os/exec"
)

// NodeServer实现CSI Node Service
type NodeServer struct {
 driver *Driver
 nodeID string
}

// NodeStageVolume挂载卷到全局目录 (staging)
func (ns *NodeServer) NodeStageVolume(
 ctx context.Context,
 req *csi.NodeStageVolumeRequest,
) (*csi.NodeStageVolumeResponse, error) {
 volumeID := req.GetVolumeId()
 stagingTargetPath := req.GetStagingTargetPath()
 
 // 1. 验证参数
 if volumeID == "" {
  return nil, status.Error(codes.InvalidArgument, "Volume ID missing in request")
 }
 if stagingTargetPath == "" {
  return nil, status.Error(codes.InvalidArgument, "Staging target path missing in request")
 }

 // 2. 获取设备路径 (从PublishContext)
 devicePath := req.GetPublishContext()["devicePath"]

 // 3. 格式化文件系统 (如果需要)
 fsType := req.GetVolumeCapability().GetMount().GetFsType()
 if fsType == "" {
  fsType = "ext4"
 }

 // 检查是否已格式化
 cmd := exec.Command("blkid", "-p", "-s", "TYPE", "-o", "value", devicePath)
 output, err := cmd.Output()
 if err != nil || string(output) == "" {
  // 未格式化，执行格式化
  cmd = exec.Command("mkfs."+fsType, devicePath)
  if err := cmd.Run(); err != nil {
   return nil, status.Errorf(codes.Internal, "Failed to format device: %v", err)
  }
 }

 // 4. 创建staging目录
 if err := os.MkdirAll(stagingTargetPath, 0750); err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to create staging path: %v", err)
 }

 // 5. 挂载到staging目录
 cmd = exec.Command("mount", devicePath, stagingTargetPath)
 if err := cmd.Run(); err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to mount device: %v", err)
 }

 return &csi.NodeStageVolumeResponse{}, nil
}

// NodeUnstageVolume卸载卷 (unstaging)
func (ns *NodeServer) NodeUnstageVolume(
 ctx context.Context,
 req *csi.NodeUnstageVolumeRequest,
) (*csi.NodeUnstageVolumeResponse, error) {
 volumeID := req.GetVolumeId()
 stagingTargetPath := req.GetStagingTargetPath()

 // 卸载
 cmd := exec.Command("umount", stagingTargetPath)
 if err := cmd.Run(); err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to unmount: %v", err)
 }

 // 删除目录
 os.RemoveAll(stagingTargetPath)

 return &csi.NodeUnstageVolumeResponse{}, nil
}

// NodePublishVolume挂载卷到Pod (bind mount)
func (ns *NodeServer) NodePublishVolume(
 ctx context.Context,
 req *csi.NodePublishVolumeRequest,
) (*csi.NodePublishVolumeResponse, error) {
 volumeID := req.GetVolumeId()
 targetPath := req.GetTargetPath()
 stagingTargetPath := req.GetStagingTargetPath()

 // 创建目标目录
 if err := os.MkdirAll(targetPath, 0750); err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to create target path: %v", err)
 }

 // Bind mount从staging到target
 options := []string{"bind"}
 if req.GetReadonly() {
  options = append(options, "ro")
 }

 cmd := exec.Command("mount", "--bind", stagingTargetPath, targetPath)
 if err := cmd.Run(); err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to bind mount: %v", err)
 }

 return &csi.NodePublishVolumeResponse{}, nil
}

// NodeUnpublishVolume卸载Pod卷
func (ns *NodeServer) NodeUnpublishVolume(
 ctx context.Context,
 req *csi.NodeUnpublishVolumeRequest,
) (*csi.NodeUnpublishVolumeResponse, error) {
 targetPath := req.GetTargetPath()

 // 卸载
 cmd := exec.Command("umount", targetPath)
 if err := cmd.Run(); err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to unmount: %v", err)
 }

 // 删除目录
 os.RemoveAll(targetPath)

 return &csi.NodeUnpublishVolumeResponse{}, nil
}

// NodeExpandVolume节点扩容
func (ns *NodeServer) NodeExpandVolume(
 ctx context.Context,
 req *csi.NodeExpandVolumeRequest,
) (*csi.NodeExpandVolumeResponse, error) {
 volumePath := req.GetVolumePath()
 requiredBytes := req.GetCapacityRange().GetRequiredBytes()

 // 扩容文件系统
 cmd := exec.Command("resize2fs", volumePath)
 if err := cmd.Run(); err != nil {
  return nil, status.Errorf(codes.Internal, "Failed to expand filesystem: %v", err)
 }

 return &csi.NodeExpandVolumeResponse{
  CapacityBytes: requiredBytes,
 }, nil
}

// NodeGetCapabilities返回Node能力
func (ns *NodeServer) NodeGetCapabilities(
 ctx context.Context,
 req *csi.NodeGetCapabilitiesRequest,
) (*csi.NodeGetCapabilitiesResponse, error) {
 return &csi.NodeGetCapabilitiesResponse{
  Capabilities: []*csi.NodeServiceCapability{
   {
    Type: &csi.NodeServiceCapability_Rpc{
     Rpc: &csi.NodeServiceCapability_RPC{
      Type: csi.NodeServiceCapability_RPC_STAGE_UNSTAGE_VOLUME,
     },
    },
   },
   {
    Type: &csi.NodeServiceCapability_Rpc{
     Rpc: &csi.NodeServiceCapability_RPC{
      Type: csi.NodeServiceCapability_RPC_EXPAND_VOLUME,
     },
    },
   },
   {
    Type: &csi.NodeServiceCapability_Rpc{
     Rpc: &csi.NodeServiceCapability_RPC{
      Type: csi.NodeServiceCapability_RPC_GET_VOLUME_STATS,
     },
    },
   },
  },
 }, nil
}

// NodeGetInfo返回节点信息
func (ns *NodeServer) NodeGetInfo(
 ctx context.Context,
 req *csi.NodeGetInfoRequest,
) (*csi.NodeGetInfoResponse, error) {
 return &csi.NodeGetInfoResponse{
  NodeId: ns.nodeID,
  AccessibleTopology: &csi.Topology{
   Segments: map[string]string{
    "topology.kubernetes.io/region": "us-east-1",
    "topology.kubernetes.io/zone":   "us-east-1a",
   },
  },
  MaxVolumesPerNode: 100,
 }, nil
}
```

---

## 3. 常用CSI驱动

### 3.1 Rook CSI for Ceph

**部署Rook CSI**:

```yaml
# Rook CSI自动部署 (随Rook Operator)
# RBD StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-ceph-block
provisioner: rook-ceph.rbd.csi.ceph.com
parameters:
  clusterID: rook-ceph
  pool: replicapool
  imageFormat: "2"
  imageFeatures: layering
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph
  csi.storage.k8s.io/controller-expand-secret-name: rook-csi-rbd-provisioner
  csi.storage.k8s.io/controller-expand-secret-namespace: rook-ceph
  csi.storage.k8s.io/node-stage-secret-name: rook-csi-rbd-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph
  csi.storage.k8s.io/fstype: ext4
allowVolumeExpansion: true
reclaimPolicy: Delete

---
# CephFS StorageClass
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: rook-cephfs
provisioner: rook-ceph.cephfs.csi.ceph.com
parameters:
  clusterID: rook-ceph
  fsName: myfs
  pool: myfs-data0
  csi.storage.k8s.io/provisioner-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/provisioner-secret-namespace: rook-ceph
  csi.storage.k8s.io/controller-expand-secret-name: rook-csi-cephfs-provisioner
  csi.storage.k8s.io/controller-expand-secret-namespace: rook-ceph
  csi.storage.k8s.io/node-stage-secret-name: rook-csi-cephfs-node
  csi.storage.k8s.io/node-stage-secret-namespace: rook-ceph
allowVolumeExpansion: true
reclaimPolicy: Delete
```

**使用Rook CSI**:

```yaml
# RBD PVC
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: rbd-pvc
spec:
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: rook-ceph-block

---
# CephFS PVC (ReadWriteMany)
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cephfs-pvc
spec:
  accessModes:
  - ReadWriteMany
  resources:
    requests:
      storage: 10Gi
  storageClassName: rook-cephfs
```

---

### 3.2 CSI for NFS

**部署NFS CSI**:

```bash
# 使用Helm安装
helm repo add csi-driver-nfs https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/charts
helm install csi-driver-nfs csi-driver-nfs/csi-driver-nfs \
  --namespace kube-system \
  --version v4.5.0
```

**StorageClass配置**:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-csi
provisioner: nfs.csi.k8s.io
parameters:
  server: nfs-server.default.svc.cluster.local
  share: /export/k8s
mountOptions:
  - nfsvers=4.1
reclaimPolicy: Delete
volumeBindingMode: Immediate
```

---

### 3.3 CSI HostPath

**CSI HostPath Driver** (仅用于开发/测试):

```bash
# 部署CSI HostPath
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-host-path/master/deploy/kubernetes-latest/hostpath/csi-hostpath-driverinfo.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-host-path/master/deploy/kubernetes-latest/hostpath/csi-hostpath-plugin.yaml
kubectl apply -f https://raw.githubusercontent.com/kubernetes-csi/csi-driver-host-path/master/deploy/kubernetes-latest/hostpath/csi-hostpath-storageclass.yaml
```

---

### 3.4 云厂商CSI

**AWS EBS CSI**:

```bash
# 安装AWS EBS CSI
kubectl apply -k "github.com/kubernetes-sigs/aws-ebs-csi-driver/deploy/kubernetes/overlays/stable/?ref=release-1.25"
```

**Azure Disk CSI**:

```bash
# 安装Azure Disk CSI
kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/azuredisk-csi-driver/master/deploy/install-driver.sh
```

**GCE PD CSI**:

```bash
# GKE默认启用，手动安装:
kubectl apply -k "github.com/kubernetes-sigs/gcp-compute-persistent-disk-csi-driver/deploy/kubernetes/overlays/stable"
```

---

## 4. CSI高级特性

### 4.1 Volume Snapshot

**创建VolumeSnapshotClass**:

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-hostpath-snapclass
driver: hostpath.csi.k8s.io
deletionPolicy: Delete
```

**创建VolumeSnapshot**:

```yaml
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: my-snapshot
spec:
  volumeSnapshotClassName: csi-hostpath-snapclass
  source:
    persistentVolumeClaimName: my-pvc
```

**从快照恢复**:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: restored-pvc
spec:
  dataSource:
    name: my-snapshot
    kind: VolumeSnapshot
    apiGroup: snapshot.storage.k8s.io
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: csi-hostpath-sc
```

---

### 4.2 Volume Clone

**克隆PVC**:

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: cloned-pvc
spec:
  dataSource:
    name: source-pvc
    kind: PersistentVolumeClaim
  accessModes:
  - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  storageClassName: rook-ceph-block
```

---

### 4.3 Volume Resize

**在线扩容**:

```bash
# 1. 确认StorageClass支持扩容
kubectl get sc rook-ceph-block -o jsonpath='{.allowVolumeExpansion}'
# true

# 2. 扩容PVC
kubectl patch pvc my-pvc -p '{"spec":{"resources":{"requests":{"storage":"20Gi"}}}}'

# 3. 查看扩容状态
kubectl get pvc my-pvc -w
```

---

### 4.4 Topology感知

**拓扑感知StorageClass**:

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: topology-aware-sc
provisioner: rook-ceph.rbd.csi.ceph.com
parameters:
  ...
volumeBindingMode: WaitForFirstConsumer  # 延迟绑定
allowedTopologies:
- matchLabelExpressions:
  - key: topology.kubernetes.io/zone
    values:
    - us-east-1a
    - us-east-1b
```

---

## 5. 最佳实践

### 5.1 性能优化

```yaml
优化建议:
  1. 使用本地存储 (LocalPV)
  2. 启用ReadWriteMany (CephFS)
  3. 调整I/O调度器
  4. 使用SSD
  5. 网络优化 (10GbE+)
```

---

### 5.2 安全加固

```yaml
安全建议:
  ✅ RBAC最小权限
  ✅ 加密静态数据
  ✅ 加密传输
  ✅ Secret管理
  ✅ 审计日志
```

---

### 5.3 故障排查

```bash
# 查看CSI Pod日志
kubectl -n kube-system logs csi-xxx-controller-0 -c csi-provisioner
kubectl -n kube-system logs csi-xxx-controller-0 -c csi-attacher
kubectl -n kube-system logs csi-xxx-node-xxx -c csi-driver

# 查看PV/PVC事件
kubectl describe pvc my-pvc
kubectl describe pv pvc-xxx

# 查看VolumeAttachment
kubectl get volumeattachment
kubectl describe volumeattachment csi-xxx
```

---

## 6. 总结

```yaml
核心知识:
  ✅ CSI架构与规范
  ✅ Identity/Controller/Node Service
  ✅ CSI插件开发 (Go代码)
  ✅ 常用CSI驱动 (Rook/NFS/HostPath)
  ✅ CSI高级特性 (Snapshot/Clone/Resize/Topology)
  ✅ 最佳实践

代码示例:
  - Go代码 (Identity/Controller/Node Service)
  - YAML配置 (StorageClass/PVC/Snapshot)
  - Helm安装
```

---

**完成日期**: 2025-10-19  
**版本**: v1.0  
**作者**: 云原生存储专家团队

**Tags**: `#CSI` `#ContainerStorageInterface` `#Kubernetes` `#Storage` `#CloudNative`
