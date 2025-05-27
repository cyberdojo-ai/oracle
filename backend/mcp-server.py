from src.mcp import app


if __name__ == "__main__":
    app.settings.host = "0.0.0.0"
    app.run(transport="sse")
