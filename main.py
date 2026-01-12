from src.index import server

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app=server.streamable_http_app(),
        host="0.0.0.0",
        port=8080,
        log_level="info",
        reload=False,
    )