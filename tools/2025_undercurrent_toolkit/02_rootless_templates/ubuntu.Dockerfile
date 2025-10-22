# ===================================================================
# Rootless Ubuntu模板 (~30MB)
# ===================================================================
# 特性:
#   ✅ 零Capabilities
#   ✅ 非root用户
#   ✅ 只读根文件系统
#   ✅ apt包管理
# ===================================================================

FROM ubuntu:22.04

# 创建非特权用户
RUN groupadd -g 1000 appuser && \
    useradd -m -u 1000 -g appuser appuser

# 安装依赖 (作为root)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        curl && \
    rm -rf /var/lib/apt/lists/*

# 切换到非root用户
USER appuser

# 工作目录
WORKDIR /home/appuser

# 复制应用
COPY --chown=appuser:appuser app /home/appuser/app

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD /home/appuser/app --health || exit 1

# 启动命令
CMD ["./app"]

# ===================================================================
# 构建与验证:
#   docker build -t myapp:rootless -f ubuntu.Dockerfile .
#   docker run --rm --cap-drop=ALL --read-only \
#       --tmpfs /tmp myapp:rootless
# ===================================================================

