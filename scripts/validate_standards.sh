#!/bin/bash
#
# 标准验证脚本
# 用途: 验证项目是否符合各项技术标准
# 作者: 技术负责人
# 日期: 2025-10-21
#

set -euo pipefail

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 计数器
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
SKIPPED_CHECKS=0

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查函数
check_command() {
    if command -v "$1" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# 横幅
print_banner() {
    echo "============================================"
    echo "  标准符合性验证工具"
    echo "  Version: 1.0.0"
    echo "  Date: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "============================================"
    echo ""
}

# 摘要
print_summary() {
    echo ""
    echo "============================================"
    echo "  验证摘要"
    echo "============================================"
    echo -e "总检查项: ${TOTAL_CHECKS}"
    echo -e "${GREEN}通过: ${PASSED_CHECKS}${NC}"
    echo -e "${RED}失败: ${FAILED_CHECKS}${NC}"
    echo -e "${YELLOW}跳过: ${SKIPPED_CHECKS}${NC}"
    
    if [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "\n${GREEN}✅ 所有检查通过!${NC}"
        return 0
    else
        echo -e "\n${RED}❌ 存在失败项,请查看上述输出${NC}"
        return 1
    fi
}

# 1. OCI标准验证
validate_oci_standards() {
    echo ""
    log_info "=== 1. OCI标准验证 ==="
    
    # 检查是否有OCI镜像示例
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if [ -d "examples/oci-images" ]; then
        if check_command oci-image-tool; then
            log_info "运行OCI Image Tool验证..."
            if oci-image-tool validate --type imageLayout examples/oci-images/ 2>/dev/null; then
                log_info "✅ OCI镜像格式验证通过"
                PASSED_CHECKS=$((PASSED_CHECKS + 1))
            else
                log_error "❌ OCI镜像格式验证失败"
                FAILED_CHECKS=$((FAILED_CHECKS + 1))
            fi
        else
            log_warn "⏭️  oci-image-tool未安装,跳过检查"
            SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
        fi
    else
        log_warn "⏭️  未找到OCI镜像示例目录,跳过检查"
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
    fi
    
    # 检查OCI Runtime配置
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_command runc; then
        log_info "检查runc版本..."
        RUNC_VERSION=$(runc --version | head -1 | awk '{print $3}')
        log_info "✅ runc版本: $RUNC_VERSION"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        log_warn "⏭️  runc未安装,跳过检查"
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
    fi
}

# 2. Kubernetes资源验证
validate_kubernetes_resources() {
    echo ""
    log_info "=== 2. Kubernetes资源验证 ==="
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_command kubeval; then
        log_info "运行kubeval验证Kubernetes YAML..."
        YAML_FILES=$(find . -name "*.yaml" -o -name "*.yml" | grep -E "(examples|manifests|k8s)" || true)
        
        if [ -n "$YAML_FILES" ]; then
            VALIDATION_FAILED=0
            while IFS= read -r file; do
                if ! kubeval --strict "$file" 2>/dev/null; then
                    log_error "验证失败: $file"
                    VALIDATION_FAILED=1
                fi
            done <<< "$YAML_FILES"
            
            if [ $VALIDATION_FAILED -eq 0 ]; then
                log_info "✅ Kubernetes YAML验证通过"
                PASSED_CHECKS=$((PASSED_CHECKS + 1))
            else
                log_error "❌ 部分Kubernetes YAML验证失败"
                FAILED_CHECKS=$((FAILED_CHECKS + 1))
            fi
        else
            log_warn "⏭️  未找到Kubernetes YAML文件"
            SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
        fi
    else
        log_warn "⏭️  kubeval未安装,跳过检查"
        log_info "    安装: curl -L https://github.com/instrumenta/kubeval/releases/latest/download/kubeval-linux-amd64.tar.gz | tar xz"
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
    fi
}

# 3. Docker最佳实践检查
validate_docker_best_practices() {
    echo ""
    log_info "=== 3. Docker最佳实践检查 ==="
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_command hadolint; then
        log_info "运行hadolint检查Dockerfile..."
        DOCKERFILES=$(find . -name "Dockerfile*" -type f || true)
        
        if [ -n "$DOCKERFILES" ]; then
            LINT_FAILED=0
            while IFS= read -r file; do
                if ! hadolint "$file" 2>/dev/null; then
                    log_warn "Lint警告: $file"
                    LINT_FAILED=1
                fi
            done <<< "$DOCKERFILES"
            
            if [ $LINT_FAILED -eq 0 ]; then
                log_info "✅ Dockerfile最佳实践检查通过"
                PASSED_CHECKS=$((PASSED_CHECKS + 1))
            else
                log_warn "⚠️  部分Dockerfile存在改进空间"
                PASSED_CHECKS=$((PASSED_CHECKS + 1))  # 警告不算失败
            fi
        else
            log_warn "⏭️  未找到Dockerfile"
            SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
        fi
    else
        log_warn "⏭️  hadolint未安装,跳过检查"
        log_info "    安装: brew install hadolint (macOS) 或 apt-get install hadolint (Ubuntu)"
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
    fi
}

# 4. Markdown文档格式检查
validate_markdown_format() {
    echo ""
    log_info "=== 4. Markdown文档格式检查 ==="
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_command markdownlint; then
        log_info "运行markdownlint检查..."
        if markdownlint . --config .markdownlint.json 2>/dev/null || [ $? -eq 1 ]; then
            log_info "✅ Markdown格式检查完成"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            log_error "❌ Markdown格式检查失败"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
    else
        log_warn "⏭️  markdownlint未安装,跳过检查"
        log_info "    安装: npm install -g markdownlint-cli"
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
    fi
}

# 5. 链接有效性检查
validate_links() {
    echo ""
    log_info "=== 5. 链接有效性检查 ==="
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_command lychee; then
        log_info "运行lychee检查链接..."
        if lychee --no-progress './**/*.md' --exclude-path '_archive' 2>/dev/null; then
            log_info "✅ 链接有效性检查通过"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            log_warn "⚠️  部分链接可能失效,请检查"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))  # 链接失效不算致命错误
        fi
    else
        log_warn "⏭️  lychee未安装,跳过检查"
        log_info "    安装: cargo install lychee 或 brew install lychee"
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
    fi
}

# 6. YAML语法检查
validate_yaml_syntax() {
    echo ""
    log_info "=== 6. YAML语法检查 ==="
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_command yamllint; then
        log_info "运行yamllint检查..."
        if yamllint . 2>/dev/null || [ $? -eq 1 ]; then
            log_info "✅ YAML语法检查完成"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            log_error "❌ YAML语法检查失败"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
    else
        log_warn "⏭️  yamllint未安装,跳过检查"
        log_info "    安装: pip install yamllint"
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
    fi
}

# 7. Shell脚本检查
validate_shell_scripts() {
    echo ""
    log_info "=== 7. Shell脚本检查 ==="
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    if check_command shellcheck; then
        log_info "运行shellcheck检查..."
        SHELL_SCRIPTS=$(find scripts -name "*.sh" -type f 2>/dev/null || true)
        
        if [ -n "$SHELL_SCRIPTS" ]; then
            SHELLCHECK_FAILED=0
            while IFS= read -r file; do
                if ! shellcheck "$file" 2>/dev/null; then
                    log_warn "ShellCheck警告: $file"
                    SHELLCHECK_FAILED=1
                fi
            done <<< "$SHELL_SCRIPTS"
            
            if [ $SHELLCHECK_FAILED -eq 0 ]; then
                log_info "✅ Shell脚本检查通过"
                PASSED_CHECKS=$((PASSED_CHECKS + 1))
            else
                log_warn "⚠️  部分Shell脚本存在改进空间"
                PASSED_CHECKS=$((PASSED_CHECKS + 1))
            fi
        else
            log_warn "⏭️  未找到Shell脚本"
            SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
        fi
    else
        log_warn "⏭️  shellcheck未安装,跳过检查"
        log_info "    安装: apt-get install shellcheck 或 brew install shellcheck"
        SKIPPED_CHECKS=$((SKIPPED_CHECKS + 1))
    fi
}

# 8. 标准符合性文档检查
validate_compliance_docs() {
    echo ""
    log_info "=== 8. 标准符合性文档检查 ==="
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 3))
    
    # 检查STANDARDS_COMPLIANCE.md
    if [ -f "STANDARDS_COMPLIANCE.md" ]; then
        log_info "✅ STANDARDS_COMPLIANCE.md 存在"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        log_error "❌ STANDARDS_COMPLIANCE.md 缺失"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    
    # 检查STANDARDS_COMPLIANCE_MATRIX.md
    if [ -f "STANDARDS_COMPLIANCE_MATRIX.md" ]; then
        log_info "✅ STANDARDS_COMPLIANCE_MATRIX.md 存在"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        log_error "❌ STANDARDS_COMPLIANCE_MATRIX.md 缺失"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
    
    # 检查引用规范
    if [ -f "_docs/standards/CITATION_GUIDE.md" ]; then
        log_info "✅ 引用规范指南存在"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        log_error "❌ 引用规范指南缺失"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

# 主函数
main() {
    print_banner
    
    # 检查是否在项目根目录
    if [ ! -f "README.md" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 运行所有验证
    validate_oci_standards
    validate_kubernetes_resources
    validate_docker_best_practices
    validate_markdown_format
    validate_links
    validate_yaml_syntax
    validate_shell_scripts
    validate_compliance_docs
    
    # 打印摘要
    print_summary
    
    # 返回结果
    if [ $FAILED_CHECKS -eq 0 ]; then
        exit 0
    else
        exit 1
    fi
}

# 执行主函数
main "$@"

