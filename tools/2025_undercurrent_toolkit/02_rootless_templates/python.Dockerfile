# ===================================================================
# Rootless Python模板 (~50MB)
# ===================================================================
# 特性:
#   ✅ 零Capabilities
#   ✅ 非root用户
#   ✅ 只读根文件系统
#   ✅ pip用户安装
# ===================================================================

FROM python:3.11-alpine

# 创建非特权用户
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# 切换到非root用户
USER appuser

# 工作目录
WORKDIR /home/appuser

# 复制requirements
COPY --chown=appuser:appuser requirements.txt .

# 用户级别安装依赖
RUN pip install --user --no-cache-dir -r requirements.txt

# 复制应用代码
COPY --chown=appuser:appuser app.py .
COPY --chown=appuser:appuser ./src ./src

# 设置PATH (用户级别pip安装)
ENV PATH="/home/appuser/.local/bin:$PATH"

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# 启动命令
CMD ["python", "app.py"]

# ===================================================================
# 构建与验证:
#   docker build -t myapp:rootless -f python.Dockerfile .
#   docker run --rm --cap-drop=ALL --read-only \
#       --tmpfs /tmp --tmpfs /home/appuser/.cache \
#       myapp:rootless
# ===================================================================

