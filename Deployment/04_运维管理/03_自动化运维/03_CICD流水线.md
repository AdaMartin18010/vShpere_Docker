# CI/CD流水线

> **返回**: [自动化运维首页](README.md) | [运维管理首页](../README.md) | [部署指南首页](../../00_索引导航/README.md)

---

## 📋 目录

- [CI/CD流水线](#cicd流水线)
  - [📋 目录](#-目录)
  - [1. GitLab CI](#1-gitlab-ci)
  - [2. ArgoCD GitOps](#2-argocd-gitops)
  - [3. 流水线最佳实践](#3-流水线最佳实践)

---

## 1. GitLab CI

**.gitlab-ci.yml**:

```yaml
stages:
  - build
  - test
  - deploy

variables:
  DOCKER_REGISTRY: registry.example.com
  IMAGE_NAME: $DOCKER_REGISTRY/myapp

build:
  stage: build
  script:
    - docker build -t $IMAGE_NAME:$CI_COMMIT_SHA .
    - docker push $IMAGE_NAME:$CI_COMMIT_SHA

test:
  stage: test
  script:
    - npm test

deploy-prod:
  stage: deploy
  script:
    - kubectl set image deployment/myapp myapp=$IMAGE_NAME:$CI_COMMIT_SHA
  only:
    - main
```

---

## 2. ArgoCD GitOps

**安装ArgoCD**:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

**Application定义**:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: myapp
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/myapp
    targetRevision: HEAD
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: production
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

---

## 3. 流水线最佳实践

**多环境部署**:

```yaml
# dev环境
deploy-dev:
  stage: deploy
  environment:
    name: development
  only:
    - develop

# prod环境  
deploy-prod:
  stage: deploy
  environment:
    name: production
  when: manual
  only:
    - main
```

**镜像安全扫描**:

```yaml
security-scan:
  stage: test
  script:
    - trivy image --severity HIGH,CRITICAL $IMAGE_NAME:$CI_COMMIT_SHA
```

---

**更新时间**: 2025-10-19  
**文档版本**: v1.0  
**状态**: ✅ 完成
