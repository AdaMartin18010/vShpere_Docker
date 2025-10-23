# 🖥️ 虚拟化API测试覆盖矩阵

> **虚拟化平台**: VMware vSphere, libvirt, QEMU  
> **最后更新**: 2025年10月23日

---

## 📊 VMware vSphere API 完整功能覆盖矩阵

### 1. 虚拟机管理 (Virtual Machine Management)

#### 1.1 虚拟机生命周期 (VM Lifecycle)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **创建VM** | 基础创建 | 最小配置创建VM | ❌ |
| | 完整配置创建 | CPU/内存/磁盘/网络 | ❌ |
| | 从模板创建 | 基于模板克隆 | ❌ |
| | 从OVF创建 | 导入OVF/OVA | ❌ |
| | 自定义硬件 | 指定硬件版本 | ❌ |
| **启动VM** | 正常启动 | Power On | ❌ |
| | 强制启动 | Force Power On | ❌ |
| | 挂起后启动 | Resume from suspend | ❌ |
| **停止VM** | 优雅关机 | Guest Shutdown | ❌ |
| | 强制关机 | Power Off | ❌ |
| | 挂起 | Suspend | ❌ |
| **重启VM** | 优雅重启 | Guest Reboot | ❌ |
| | 强制重启 | Reset | ❌ |
| **删除VM** | 删除VM | Destroy VM | ❌ |
| | 从存储删除 | Delete from disk | ❌ |
| | 保留磁盘 | Remove but keep disks | ❌ |

#### 1.2 虚拟机配置 (VM Configuration)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **CPU配置** | 设置CPU数量 | vCPU count | ❌ |
| | CPU热添加 | Hot-add CPU | ❌ |
| | CPU预留 | CPU reservation | ❌ |
| | CPU限制 | CPU limit | ❌ |
| | CPU亲和性 | CPU affinity | ❌ |
| **内存配置** | 设置内存大小 | Memory size | ❌ |
| | 内存热添加 | Hot-add memory | ❌ |
| | 内存预留 | Memory reservation | ❌ |
| | 内存限制 | Memory limit | ❌ |
| | 内存共享 | Memory shares | ❌ |
| **磁盘配置** | 添加虚拟磁盘 | Add virtual disk | ❌ |
| | 扩展磁盘 | Extend disk | ❌ |
| | 删除磁盘 | Remove disk | ❌ |
| | 厚置备 | Thick provisioning | ❌ |
| | 精简置备 | Thin provisioning | ❌ |
| | 快照磁盘 | Snapshot disk | ❌ |
| **网络配置** | 添加网卡 | Add network adapter | ❌ |
| | 删除网卡 | Remove adapter | ❌ |
| | 修改网络 | Change network | ❌ |
| | 网卡类型 | Adapter type (e1000, vmxnet3) | ❌ |
| | MAC地址 | Custom MAC address | ❌ |

#### 1.3 虚拟机快照 (VM Snapshot)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **创建快照** | 标准快照 | Create snapshot | ❌ |
| | 包含内存 | Snapshot with memory | ❌ |
| | 静默快照 | Quiesce snapshot | ❌ |
| | 描述信息 | Snapshot with description | ❌ |
| **快照操作** | 恢复快照 | Revert to snapshot | ❌ |
| | 删除快照 | Remove snapshot | ❌ |
| | 删除所有快照 | Remove all snapshots | ❌ |
| | 合并快照 | Consolidate snapshots | ❌ |
| **快照管理** | 列出快照 | List snapshots | ❌ |
| | 快照树 | Snapshot tree | ❌ |
| | 快照大小 | Snapshot size | ❌ |

#### 1.4 虚拟机克隆 (VM Clone)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **完整克隆** | 克隆VM | Full clone | ❌ |
| | 跨存储克隆 | Clone to different datastore | ❌ |
| | 跨主机克隆 | Clone to different host | ❌ |
| **链接克隆** | 创建链接克隆 | Linked clone | ❌ |
| | 从快照克隆 | Clone from snapshot | ❌ |
| **模板** | 转换为模板 | Convert to template | ❌ |
| | 从模板部署 | Deploy from template | ❌ |

#### 1.5 虚拟机迁移 (VM Migration)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **vMotion** | 热迁移 | Live migration | ❌ |
| | 跨主机迁移 | Cross-host migration | ❌ |
| | 跨集群迁移 | Cross-cluster migration | ❌ |
| **Storage vMotion** | 存储迁移 | Storage migration | ❌ |
| | 在线存储迁移 | Online storage migration | ❌ |
| **冷迁移** | 离线迁移 | Cold migration | ❌ |

### 2. ESXi主机管理 (ESXi Host Management)

#### 2.1 主机操作

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **主机信息** | 获取主机信息 | Host properties | ❌ |
| | 硬件信息 | Hardware info | ❌ |
| | 系统信息 | System info | ❌ |
| **主机状态** | 进入维护模式 | Enter maintenance mode | ❌ |
| | 退出维护模式 | Exit maintenance mode | ❌ |
| | 重启主机 | Reboot host | ❌ |
| | 关闭主机 | Shutdown host | ❌ |
| **资源监控** | CPU使用率 | CPU usage | ❌ |
| | 内存使用率 | Memory usage | ❌ |
| | 存储使用 | Storage usage | ❌ |
| | 网络流量 | Network traffic | ❌ |

### 3. 存储管理 (Storage Management)

#### 3.1 数据存储 (Datastore)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **数据存储操作** | 列出数据存储 | List datastores | ❌ |
| | 挂载数据存储 | Mount datastore | ❌ |
| | 卸载数据存储 | Unmount datastore | ❌ |
| | 重命名数据存储 | Rename datastore | ❌ |
| **存储类型** | VMFS | VMFS datastore | ❌ |
| | NFS | NFS datastore | ❌ |
| | vSAN | vSAN datastore | ❌ |
| **文件操作** | 上传文件 | Upload to datastore | ❌ |
| | 下载文件 | Download from datastore | ❌ |
| | 删除文件 | Delete file | ❌ |
| | 创建目录 | Create directory | ❌ |

### 4. 网络管理 (Network Management)

#### 4.1 虚拟交换机 (Virtual Switch)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **标准交换机** | 创建vSwitch | Create standard switch | ❌ |
| | 删除vSwitch | Remove switch | ❌ |
| | 添加端口组 | Add port group | ❌ |
| | 配置VLAN | Configure VLAN | ❌ |
| **分布式交换机** | 创建dvSwitch | Create distributed switch | ❌ |
| | 添加主机 | Add host to dvSwitch | ❌ |
| | 配置dvPortGroup | Configure distributed port group | ❌ |

### 5. 资源池 (Resource Pool)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **资源池操作** | 创建资源池 | Create resource pool | ❌ |
| | 删除资源池 | Remove resource pool | ❌ |
| | 配置份额 | Configure shares | ❌ |
| | 配置预留 | Configure reservation | ❌ |
| | 配置限制 | Configure limit | ❌ |

---

## 🔧 libvirt API 完整功能覆盖矩阵

### 1. 域管理 (Domain Management)

#### 1.1 域生命周期 (Domain Lifecycle)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **创建域** | 定义域 | Define domain | ❌ |
| | 从XML创建 | Create from XML | ❌ |
| | 瞬态域 | Transient domain | ❌ |
| **启动域** | 启动 | Domain start | ❌ |
| | 自动启动 | Autostart | ❌ |
| | 暂停启动 | Start paused | ❌ |
| **停止域** | 关闭 | Shutdown | ❌ |
| | 强制停止 | Destroy | ❌ |
| | 挂起 | Suspend | ❌ |
| | 恢复 | Resume | ❌ |
| **重启域** | 重启 | Reboot | ❌ |
| | 重置 | Reset | ❌ |
| **删除域** | 取消定义 | Undefine | ❌ |
| | 删除快照 | Undefine with snapshots | ❌ |

#### 1.2 域配置 (Domain Configuration)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **CPU配置** | 设置vCPU | Set vCPU count | ❌ |
| | CPU拓扑 | CPU topology | ❌ |
| | CPU绑定 | CPU pinning | ❌ |
| **内存配置** | 设置内存 | Set memory | ❌ |
| | 最大内存 | Maximum memory | ❌ |
| | 内存气球 | Memory balloon | ❌ |
| **磁盘配置** | 附加磁盘 | Attach disk | ❌ |
| | 分离磁盘 | Detach disk | ❌ |
| | 块设备 | Block device | ❌ |
| | 文件设备 | File device | ❌ |
| **网络配置** | 附加网卡 | Attach interface | ❌ |
| | 分离网卡 | Detach interface | ❌ |
| | 桥接网络 | Bridge network | ❌ |
| | NAT网络 | NAT network | ❌ |

#### 1.3 域快照 (Domain Snapshot)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **快照操作** | 创建快照 | Create snapshot | ❌ |
| | 删除快照 | Delete snapshot | ❌ |
| | 恢复快照 | Revert to snapshot | ❌ |
| | 列出快照 | List snapshots | ❌ |
| **快照类型** | 内部快照 | Internal snapshot | ❌ |
| | 外部快照 | External snapshot | ❌ |
| | 磁盘快照 | Disk-only snapshot | ❌ |
| | 内存快照 | Memory snapshot | ❌ |

### 2. 存储管理 (Storage Management)

#### 2.1 存储池 (Storage Pool)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **池操作** | 定义存储池 | Define pool | ❌ |
| | 创建存储池 | Build pool | ❌ |
| | 启动存储池 | Start pool | ❌ |
| | 停止存储池 | Stop pool | ❌ |
| | 删除存储池 | Delete pool | ❌ |
| | 刷新存储池 | Refresh pool | ❌ |
| **池类型** | 目录池 | Directory pool | ❌ |
| | LVM池 | LVM pool | ❌ |
| | NFS池 | NFS pool | ❌ |
| | iSCSI池 | iSCSI pool | ❌ |

#### 2.2 存储卷 (Storage Volume)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **卷操作** | 创建卷 | Create volume | ❌ |
| | 删除卷 | Delete volume | ❌ |
| | 克隆卷 | Clone volume | ❌ |
| | 调整卷大小 | Resize volume | ❌ |
| | 上传卷 | Upload volume | ❌ |
| | 下载卷 | Download volume | ❌ |
| **卷格式** | RAW格式 | RAW format | ❌ |
| | QCOW2格式 | QCOW2 format | ❌ |

### 3. 网络管理 (Network Management)

#### 3.1 虚拟网络 (Virtual Network)

| 主功能 | 子功能 | 测试场景 | 状态 |
|--------|--------|----------|------|
| **网络操作** | 定义网络 | Define network | ❌ |
| | 创建网络 | Create network | ❌ |
| | 启动网络 | Start network | ❌ |
| | 停止网络 | Stop network | ❌ |
| | 删除网络 | Delete network | ❌ |
| **网络类型** | NAT网络 | NAT network | ❌ |
| | 桥接网络 | Bridge network | ❌ |
| | 隔离网络 | Isolated network | ❌ |
| | 路由网络 | Routed network | ❌ |

---

## 🔗 虚拟化功能联动测试矩阵

### vSphere功能联动

| 主功能1 | 主功能2 | 联动场景 | 测试内容 | 状态 |
|---------|---------|----------|----------|------|
| **VM** | **Snapshot** | 快照管理 | 创建→恢复→删除 | ❌ |
| **VM** | **Clone** | VM克隆 | 完整克隆/链接克隆 | ❌ |
| **VM** | **Template** | 模板部署 | 转换模板→部署 | ❌ |
| **VM** | **vMotion** | 热迁移 | 在线迁移VM | ❌ |
| **VM** | **Datastore** | 存储管理 | VM存储迁移 | ❌ |
| **VM** | **Network** | 网络配置 | 动态更改网络 | ❌ |
| **VM** | **Resource Pool** | 资源分配 | 资源池管理 | ❌ |
| **Host** | **VM** | 主机维护 | 维护模式迁移 | ❌ |

### libvirt功能联动

| 主功能1 | 主功能2 | 联动场景 | 测试内容 | 状态 |
|---------|---------|----------|----------|------|
| **Domain** | **Snapshot** | 快照恢复 | 创建快照→恢复 | ❌ |
| **Domain** | **Storage Pool** | 存储使用 | 从池创建卷 | ❌ |
| **Domain** | **Network** | 网络连接 | 连接虚拟网络 | ❌ |
| **Domain** | **Clone** | 域克隆 | 克隆域 | ❌ |
| **Storage Pool** | **Volume** | 卷管理 | 池中创建卷 | ❌ |

---

## 📈 测试覆盖率统计

### vSphere API

- **虚拟机管理**: 0/78 (0%)
  - 生命周期: 0/18
  - 配置: 0/29
  - 快照: 0/11
  - 克隆: 0/7
  - 迁移: 0/6
- **主机管理**: 0/12 (0%)
- **存储管理**: 0/12 (0%)
- **网络管理**: 0/7 (0%)
- **资源池**: 0/5 (0%)
- **功能联动**: 0/8 (0%)
- **总体覆盖率**: 0/122 ≈ **0%**

### libvirt API

- **域管理**: 0/38 (0%)
  - 生命周期: 0/16
  - 配置: 0/14
  - 快照: 0/8
- **存储管理**: 0/20 (0%)
  - 存储池: 0/10
  - 存储卷: 0/10
- **网络管理**: 0/9 (0%)
- **功能联动**: 0/5 (0%)
- **总体覆盖率**: 0/72 ≈ **0%**

### 总体

- **已实现**: 0
- **待实现**: 194
- **总体覆盖率**: 0/194 ≈ **0%**

---

## 🎯 优先级规划

### P0 - 核心功能 (必须实现)

- [ ] vSphere VM生命周期
- [ ] vSphere VM快照
- [ ] libvirt域生命周期
- [ ] libvirt域快照
- [ ] 存储池基础操作
- [ ] 网络基础配置

### P1 - 重要功能 (应该实现)

- [ ] VM配置完整测试
- [ ] VM克隆和模板
- [ ] vMotion迁移
- [ ] 资源池管理
- [ ] 存储卷管理
- [ ] 功能联动测试

### P2 - 扩展功能 (可以实现)

- [ ] 高级网络配置
- [ ] 分布式交换机
- [ ] 集群管理
- [ ] 高可用性

---

**最后更新**: 2025年10月23日  
**维护团队**: 虚拟化测试团队
