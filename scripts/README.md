# 自动化脚本说明

本目录包含用于自动化监控技术版本更新的脚本。

## 脚本列表

### 版本检查脚本

1. **check_k8s_version.py**
   - 检查Kubernetes版本更新
   - 从GitHub API获取最新版本
   - 与项目中的版本对比

2. **check_docker_version.py**
   - 检查Docker版本更新
   - 从GitHub API获取最新版本

3. **check_podman_version.py**
   - 检查Podman版本更新
   - 从GitHub API获取最新版本

4. **check_vsphere_version.py**
   - 检查vSphere版本更新
   - 使用预定义的已知版本
   - 需要定期手动更新

5. **generate_version_report.py**
   - 生成版本检查报告
   - Markdown格式输出
   - 包含更新建议和检查清单

## 使用方法

### 本地运行

```bash
# 安装依赖
pip install requests pyyaml beautifulsoup4

# 运行单个检查
python scripts/check_k8s_version.py

# 运行所有检查并生成报告
python scripts/check_k8s_version.py
python scripts/check_docker_version.py
python scripts/check_podman_version.py
python scripts/check_vsphere_version.py
python scripts/generate_version_report.py
```

### GitHub Actions

自动化检查通过GitHub Actions运行，配置文件位于`.github/workflows/version-monitor.yml`

**触发方式**:

- 自动: 每周一早上9点(北京时间)
- 手动: GitHub仓库页面 → Actions → Technology Version Monitor → Run workflow

**功能**:

- 自动检查版本更新
- 生成版本报告
- 创建或更新Issue提醒

## 配置

### 修改检查频率

编辑`.github/workflows/version-monitor.yml`中的cron表达式:

```yaml
schedule:
  - cron: '0 1 * * 1'  # 每周一UTC 1:00 (北京时间9:00)
```

常用cron表达式:

- `0 1 * * *` - 每天UTC 1:00
- `0 1 * * 1` - 每周一UTC 1:00
- `0 1 1 * *` - 每月1号UTC 1:00

### 添加新技术监控

1. 创建新的检查脚本 `scripts/check_xxx_version.py`
2. 在`.github/workflows/version-monitor.yml`中添加新步骤
3. 更新`generate_version_report.py`以包含新技术

## 维护

### 手动更新vSphere版本

编辑`scripts/check_vsphere_version.py`中的版本号:

```python
def get_known_latest_vsphere_version():
    return "8.0.3"  # 更新此版本号
```

### 调试

如果脚本运行失败，检查:

1. GitHub API访问是否正常
2. 文档文件路径是否正确
3. 版本号正则表达式是否匹配
4. Python依赖是否安装

## 输出

### 版本报告文件

`version_report.md` - 包含完整的版本检查结果和更新建议

### GitHub Issue

自动创建或更新带有`version-update`标签的Issue

## 注意事项

1. **GitHub API限制**: 未认证的请求限制为60次/小时
2. **网络访问**: 需要能访问GitHub API
3. **文档路径**: 脚本假设特定的文档路径和格式
4. **版本格式**: 假设语义化版本(major.minor.patch)

## 故障排除

### 问题: API请求失败

```bash
# 检查网络连接
curl -I https://api.github.com

# 检查API限制
curl https://api.github.com/rate_limit
```

### 问题: 版本号解析失败

检查文档中的版本号格式是否符合正则表达式:

- Kubernetes: `Kubernetes: 1.30.0`
- Docker: `Docker: 25.0.0`

### 问题: GitHub Actions权限

确保仓库设置中启用了:

- Settings → Actions → General → Workflow permissions → Read and write permissions

## 扩展

### 添加邮件通知

修改`.github/workflows/version-monitor.yml`，添加邮件发送步骤。

### 添加Slack通知

使用Slack webhook发送通知到Slack频道。

### 添加更多检查

参考现有脚本创建新的版本检查脚本。

---

**维护者**: 项目技术团队  
**最后更新**: 2025-10-19
