# ===================================================================
# Rootless Alpine模板 (~5MB)
# ===================================================================
# 特性:
#   ✅ 零Capabilities
#   ✅ 非root用户
#   ✅ 只读根文件系统
#   ✅ 最小化镜像
# ===================================================================

FROM alpine:3.19

# 创建非特权用户
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# 切换到非root用户
USER appuser

# 工作目录
WORKDIR /home/appuser

# 复制应用 (确保ownership)
COPY --chown=appuser:appuser app /home/appuser/app

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD /home/appuser/app --health || exit 1

# 启动命令
CMD ["./app"]

# ===================================================================
# 构建与验证:
#   docker build -t myapp:rootless -f alpine.Dockerfile .
#   docker run --rm --cap-drop=ALL --read-only myapp:rootless
# ===================================================================

