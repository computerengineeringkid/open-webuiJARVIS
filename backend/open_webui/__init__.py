"""Command line entry points for the minimal chat API."""

from __future__ import annotations

import typer
import uvicorn

app = typer.Typer()


@app.command()
def serve(host: str = "0.0.0.0", port: int = 8080, reload: bool = False) -> None:
    uvicorn.run(
        "open_webui.main:app",
        host=host,
        port=port,
        reload=reload,
    )


@app.command()
def dev(host: str = "0.0.0.0", port: int = 8080) -> None:
    serve(host=host, port=port, reload=True)


if __name__ == "__main__":
    app()
