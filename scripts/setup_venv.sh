#!/bin/bash
# Tạo môi trường ảo Python và cài đặt các phụ thuộc từ requirements.txt

# Kiểm tra python3 hoặc python đã cài chưa
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    echo "Python chưa được cài đặt!" >&2
    exit 1
fi

# Tạo môi trường ảo nếu chưa có
if [ ! -d ".venv" ]; then
    $PYTHON -m venv .venv
    echo "Đã tạo môi trường ảo .venv"
else
    echo "Môi trường ảo .venv đã tồn tại"
fi

# Kích hoạt môi trường ảo (tương thích Windows và Unix)
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" || "$OSTYPE" == "cygwin" ]]; then
    # Windows (Git Bash, MSYS, Cygwin)
    source .venv/Scripts/activate
else
    # Unix/Linux/WSL/Mac
    source .venv/bin/activate
fi

# Cài đặt các package từ requirements.txt
pip install --upgrade pip
pip install -r requirements.txt

echo "Đã cài đặt xong các phụ thuộc. Để kích hoạt môi trường ảo, hãy chạy:"
echo "Unix/Linux/Mac:   source .venv/bin/activate"
echo "Windows (Git Bash/MSYS/Cygwin): source .venv/Scripts/activate"
