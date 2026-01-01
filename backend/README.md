# CourseDesign Backend

基于 FastAPI 的后端服务。

## 环境搭建

1. 创建虚拟环境:
   ```bash
   python -m venv venv
   ```

2. 激活虚拟环境:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

3. 安装依赖:
   ```bash
   pip install -r requirements.txt
   ```

## 运行服务

```bash
python main.py
```

服务将运行在 `http://localhost:8000`。

## API 文档

运行服务后访问 `http://localhost:8000/docs` 查看 Swagger UI 文档。
