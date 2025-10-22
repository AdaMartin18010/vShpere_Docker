# ===================================================================
# Rootless Node.js模板 (~80MB)
# ===================================================================
# 特性:
#   ✅ 零Capabilities
#   ✅ 非root用户
#   ✅ 只读根文件系统
#   ✅ npm用户安装
# ===================================================================

FROM node:20-alpine

# 创建非特权用户
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser

# 切换到非root用户
USER appuser

# 工作目录
WORKDIR /home/appuser

# 复制package.json
COPY --chown=appuser:appuser package*.json ./

# 用户级别安装依赖
RUN npm install --production

# 复制应用代码
COPY --chown=appuser:appuser index.js .
COPY --chown=appuser:appuser ./src ./src

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => process.exit(r.statusCode === 200 ? 0 : 1))" || exit 1

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["node", "index.js"]

# ===================================================================
# 构建与验证:
#   docker build -t myapp:rootless -f nodejs.Dockerfile .
#   docker run --rm --cap-drop=ALL --read-only \
#       --tmpfs /tmp --tmpfs /home/appuser/.npm \
#       -p 3000:3000 myapp:rootless
# ===================================================================

