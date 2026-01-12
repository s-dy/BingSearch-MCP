FROM docker.1ms.run/library/python:3.11-slim

# 设置工作目录
WORKDIR /app

# 容器中安装 uv
RUN pip install --no-cache-dir uv

# 将主机上的依赖声明文件复制到容器中
COPY pyproject.toml .

# 容器中使用 uv 从 pyproject.toml 读取依赖并安装依赖
RUN uv pip install --system --no-cache-dir .

# 复制源代码
COPY src/ ./src/
COPY main.py .

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["python", "main.py"]
