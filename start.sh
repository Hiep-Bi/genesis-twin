#!/bin/bash

echo "🚀 Đang khởi động Genesis Twin..."

# Kiểm tra Docker
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker chưa chạy. Vui lòng khởi động Docker Desktop và thử lại."
    echo "   Hoặc chạy: open -a Docker"
    exit 1
fi

echo "✅ Docker đã sẵn sàng"

# Kiểm tra docker-compose
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose chưa được cài đặt"
    exit 1
fi

echo "📦 Đang khởi động các services..."
docker-compose up -d

echo ""
echo "⏳ Đang chờ các services khởi động..."
sleep 10

echo ""
echo "📊 Trạng thái các services:"
docker-compose ps

echo ""
echo "✅ Dự án đã được khởi động!"
echo ""
echo "🌐 Truy cập:"
echo "   - Frontend: http://localhost:3000"
echo "   - Backend API: http://localhost:8000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "🔑 Đăng nhập:"
echo "   - Username: admin@genesis.ai"
echo "   - Password: admin123"
echo ""
echo "📝 Xem logs: docker-compose logs -f [service_name]"
echo "🛑 Dừng dự án: docker-compose down"
