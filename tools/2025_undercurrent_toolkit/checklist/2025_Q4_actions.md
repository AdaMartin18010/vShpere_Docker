# 2025 Q4 抢跑行动清单 ✅

> **时间窗口**: 2025-10-22 至 2025-12-31  
> **目标ROI**: 843%  
> **总投入**: 10人日

---

## Week 1-2 (2025-10-22 至 2025-11-02)

### ⑦ 跨云镜像签名 (2人日)

- [ ] **Day 1**: 设置签名环境
  - [ ] 安装cosign (`curl -LO https://github.com/sigstore/cosign/releases/download/v2.2.0/cosign-linux-amd64`)
  - [ ] 安装syft (`curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh`)
  - [ ] 生成密钥对 (`cosign generate-key-pair`)
  - [ ] 备份私钥到安全位置

- [ ] **Day 2**: 批量签名镜像
  - [ ] 列出所有需签名的镜像 (≥50个)
  - [ ] 运行自动化脚本 (`cd tools/2025_undercurrent_toolkit/01_image_signing && ./sign_all_images.sh --all`)
  - [ ] 验证签名完整性
  - [ ] 推送签名镜像到仓库

**收益**: ¥600/年 (2026起免跨云流量费)  
**风险**: ¥5 (极低)

---

### ③ Rootless容器改造 (3人日)

- [ ] **Day 1**: 审计现有Dockerfile
  - [ ] 识别使用root用户的镜像 (≥30个)
  - [ ] 识别需要Capabilities的镜像
  - [ ] 制定改造优先级

- [ ] **Day 2**: 改造Dockerfile
  - [ ] 使用Rootless模板 (`tools/2025_undercurrent_toolkit/02_rootless_templates/`)
  - [ ] 改造Python应用 (10个)
  - [ ] 改造Node.js应用 (8个)
  - [ ] 改造Alpine应用 (12个)

- [ ] **Day 3**: 测试与验证
  - [ ] 本地测试所有Rootless镜像
  - [ ] 验证零Capabilities (`docker inspect --format='{{.Config.Capabilities}}' image`)
  - [ ] 推送Rootless镜像到仓库
  - [ ] 签名Rootless镜像 (Day 2完成后)

**收益**: ¥600/年 (2026起免Docker Hub流量费)  
**风险**: ¥2 (极低)

---

## Week 3-4 (2025-11-03 至 2025-11-16)

### ⑤ AI调度器部署 (2人日)

- [ ] **Day 1**: 升级K8s到1.32
  - [ ] 备份现有集群配置
  - [ ] 升级Master节点 (`kubeadm upgrade apply v1.32.0`)
  - [ ] 升级Worker节点
  - [ ] 验证集群健康状态

- [ ] **Day 2**: 部署AI Scheduler
  - [ ] 运行部署脚本 (`cd tools/2025_undercurrent_toolkit/03_ai_scheduler && ./deploy.sh`)
  - [ ] 配置Prometheus监控
  - [ ] 创建测试Pod (`./deploy.sh --test`)
  - [ ] 监控预测准确率 (目标: >90%)

**收益**: 集群故障率 -40%  
**风险**: ¥2 (极低)

---

### ① Firecracker试用 (2人日)

- [ ] **Day 1**: 本地部署Firecracker
  - [ ] 运行快速启动脚本 (`cd tools/2025_undercurrent_toolkit/04_firecracker && ./quick_start.sh`)
  - [ ] 测试冷启动时间 (目标: <125ms)
  - [ ] 测试容器镜像加载 (≤500MB)

- [ ] **Day 2**: 性能基准测试
  - [ ] 对比Firecracker vs Docker冷启动
  - [ ] 测试内存限制 (<512MB)
  - [ ] 记录经验与问题

**收益**: 学习曲线提前6个月  
**风险**: ¥15 (低)

---

## Week 5-8 (2025-11-17 至 2025-12-14)

### 持续监控与优化

- [ ] **每周**: 监控AI调度器效果
  - [ ] 查看故障率变化
  - [ ] 查看预测准确率
  - [ ] 调整阈值参数

- [ ] **每周**: 验证签名镜像
  - [ ] 检查所有镜像已签名
  - [ ] 检查SBOM完整性

- [ ] **每周**: 追踪标准进展
  - [ ] 关注K8s 1.32 GA (预计12月)
  - [ ] 关注Docker Hub政策更新
  - [ ] 关注云厂商流量政策

---

## Week 9-10 (2025-12-15 至 2025-12-31)

### 收尾与总结

- [ ] **收尾工作**
  - [ ] 确保所有镜像已签名 (100%)
  - [ ] 确保所有应用已Rootless (100%)
  - [ ] AI调度器稳定运行

- [ ] **ROI评估**
  - [ ] 计算实际成本 (预计: ¥0 + 10人日)
  - [ ] 计算预期收益 (预计: ¥11,200/年)
  - [ ] 更新ROI tracker

- [ ] **经验总结**
  - [ ] 记录遇到的问题与解决方案
  - [ ] 准备技术分享 (社区溢价)
  - [ ] 制定2026 Q1行动计划

---

## 关键时间点提醒 ⏰

| 日期 | 事件 | 行动 |
|------|------|------|
| 2025-11-30 | Docker Hub限速预警 | 确保80%镜像已签名 |
| 2025-12-15 | K8s 1.32 RC | 测试AI调度器 |
| 2025-12-31 | K8s 1.32 GA (预计) | 升级完成 |
| 2026-01-01 | 云厂商流量政策生效 | 确保100%镜像已签名 |

---

## 每日检查清单 📋

每天花5分钟检查：

- [ ] 今日任务是否按计划推进
- [ ] 是否遇到阻塞问题
- [ ] 是否需要调整计划
- [ ] 窗口期剩余天数 (工具: `tools/2025_undercurrent_toolkit/scripts/window_checker.sh`)

---

## 紧急联系人 🆘

- **cosign问题**: https://github.com/sigstore/cosign/issues
- **K8s升级问题**: https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/
- **Firecracker问题**: https://github.com/firecracker-microvm/firecracker/discussions

---

**更新日期**: 2025-10-22  
**状态**: ✅ 计划完整  
**下一次审查**: 2025-11-01
