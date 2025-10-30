#!/bin/bash
# 构建监控系统Docker镜像脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_header() {
    echo -e "${BLUE}"
    echo "=========================================="
    echo "🚀 构建监控系统Docker镜像"
    echo "=========================================="
    echo -e "${NC}"
}

# 检查Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker服务未运行，请启动Docker服务"
        exit 1
    fi
    
    print_success "Docker环境检查通过"
}

# 构建后端镜像
build_backend() {
    print_info "构建后端镜像..."
    
    if [ -f "Dockerfile.backend.centos7" ]; then
        docker build -f Dockerfile.backend.centos7 -t monitor-backend:latest .
    else
        docker build -f Dockerfile.backend -t monitor-backend:latest .
    fi
    
    if [ $? -eq 0 ]; then
        print_success "后端镜像构建完成: monitor-backend:latest"
    else
        print_error "后端镜像构建失败"
        exit 1
    fi
}

# 构建前端镜像
build_frontend() {
    print_info "构建前端镜像..."
    
    docker build -f Dockerfile.frontend -t monitor-frontend:latest .
    
    if [ $? -eq 0 ]; then
        print_success "前端镜像构建完成: monitor-frontend:latest"
    else
        print_error "前端镜像构建失败"
        exit 1
    fi
}

# 显示镜像信息
show_images() {
    print_info "构建完成的镜像:"
    docker images | grep monitor
    echo ""
    
    print_info "镜像大小统计:"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep monitor
}

# 主函数
main() {
    print_header
    
    check_docker
    build_backend
    build_frontend
    show_images
    
    print_success "🎉 所有镜像构建完成！"
    echo ""
    print_info "下一步操作:"
    echo "1. 配置环境变量: cp env.centos7.example .env"
    echo "2. 编辑配置文件: vim .env"
    echo "3. 启动服务: docker-compose up -d"
}

# 运行主函数
main "$@"
