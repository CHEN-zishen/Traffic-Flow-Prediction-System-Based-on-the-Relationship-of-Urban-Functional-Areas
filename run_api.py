"""启动FastAPI服务的快捷脚本"""
import uvicorn

if __name__ == "__main__":
    print("🚀 启动智能交通流预测API服务...")
    print("   访问: http://127.0.0.1:8000")
    print("   文档: http://127.0.0.1:8000/docs")
    print("   按 Ctrl+C 停止服务")
    print()
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

