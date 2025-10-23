# Makefile for Go API Tests

.PHONY: all test test-docker test-k8s test-etcd test-integration clean deps coverage help report

# 默认目标
all: test

# 安装依赖
deps:
	@echo "📦 Installing Go dependencies..."
	go mod download
	go mod tidy

# 运行所有测试
test:
	@echo "🧪 Running all API tests..."
	go test -v -timeout 30m ./...

# 运行Docker API测试
test-docker:
	@echo "🐳 Running Docker API tests..."
	go test -v -timeout 10m -run TestDockerAPI

# 运行Kubernetes API测试
test-k8s:
	@echo "☸️  Running Kubernetes API tests..."
	go test -v -timeout 15m -run TestKubernetesAPI

# 运行etcd API测试
test-etcd:
	@echo "🗄️  Running etcd API tests..."
	go test -v -timeout 10m -run TestEtcdAPI

# 运行集成测试
test-integration:
	@echo "🔗 Running integration tests..."
	go test -v -timeout 30m -run TestIntegrationSuite

# 运行测试并生成覆盖率报告
coverage:
	@echo "📊 Generating coverage report..."
	go test -v -timeout 30m -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "✅ Coverage report generated: coverage.html"

# 运行测试并输出JSON格式
test-json:
	@echo "📄 Running tests with JSON output..."
	go test -v -timeout 30m -json ./... > test-report.json

# 快速测试 (跳过长测试)
test-fast:
	@echo "⚡ Running fast tests..."
	go test -v -short -timeout 5m ./...

# 生成测试报告 (HTML + JSON + Markdown)
report: test-json
	@echo "📊 Generating test reports..."
	@if [ -f test-report.json ]; then \
		echo "✅ JSON report: test-report.json"; \
		echo "📝 To generate HTML/Markdown reports, implement report generation logic"; \
	fi

# 清理测试产物
clean:
	@echo "🧹 Cleaning test artifacts..."
	rm -f coverage.out coverage.html test-report.json
	rm -f *.prof
	rm -f report.html report.json report.md
	go clean -testcache

# 运行基准测试
bench:
	@echo "⏱️  Running benchmarks..."
	go test -bench=. -benchmem ./...

# 格式化代码
fmt:
	@echo "🎨 Formatting code..."
	go fmt ./...

# 代码检查
lint:
	@echo "🔍 Running linter..."
	@which golangci-lint > /dev/null || (echo "Installing golangci-lint..." && go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest)
	golangci-lint run

# 运行竞态检测
test-race:
	@echo "🏁 Running tests with race detector..."
	go test -v -race -timeout 30m ./...

# 运行所有检查 (格式化 + lint + 测试 + 覆盖率)
check: fmt lint test coverage
	@echo "✅ All checks passed!"

# 显示帮助信息
help:
	@echo "Go API Tests - Available targets:"
	@echo ""
	@echo "  make deps              - 安装Go依赖"
	@echo "  make test              - 运行所有API测试"
	@echo "  make test-docker       - 运行Docker API测试"
	@echo "  make test-k8s          - 运行Kubernetes API测试"
	@echo "  make test-etcd         - 运行etcd API测试"
	@echo "  make test-integration  - 运行集成测试"
	@echo "  make coverage          - 生成测试覆盖率报告"
	@echo "  make test-json         - 运行测试并输出JSON格式"
	@echo "  make test-fast         - 运行快速测试"
	@echo "  make report            - 生成测试报告"
	@echo "  make clean             - 清理测试产物"
	@echo "  make bench             - 运行基准测试"
	@echo "  make fmt               - 格式化代码"
	@echo "  make lint              - 运行代码检查"
	@echo "  make test-race         - 运行竞态检测"
	@echo "  make check             - 运行所有检查"
	@echo "  make help              - 显示此帮助信息"
	@echo ""
	@echo "环境变量:"
	@echo "  DOCKER_HOST            - Docker守护进程地址"
	@echo "  KUBECONFIG             - Kubernetes配置文件路径"
	@echo "  ETCD_ENDPOINTS         - etcd端点地址"

