# CI/CD集成配置

本目录存放各种CI/CD平台的集成配置文件。

## 支持的CI/CD平台

### GitHub Actions

配置文件: `github_actions.yml`

使用方法:

```bash
cp github_actions.yml ../../.github/workflows/api-tests.yml
```

### GitLab CI

配置文件: `gitlab_ci.yml`

使用方法:

```bash
# 合并到项目根目录的.gitlab-ci.yml
```

### Jenkins

配置文件: `jenkins_pipeline.groovy`

使用方法:

```groovy
// 在Jenkins中创建Pipeline项目
// 使用Pipeline script from SCM
// 指定本文件路径
```

## 计划创建的配置

- [ ] GitHub Actions工作流
- [ ] GitLab CI配置
- [ ] Jenkins Pipeline
- [ ] Azure DevOps Pipeline
- [ ] CircleCI配置
