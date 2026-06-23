"""Launcher: starts the local server and opens the browser."""
import threading
import time
import webbrowser

import uvicorn

HOST = "127.0.0.1"
PORT = 8080
URL = f"http://{HOST}:{PORT}"


def _open_browser():
    time.sleep(1.5)
    webbrowser.open(URL)


if __name__ == "__main__":
    print(f"\n  Saúde Pessoal — a iniciar em {URL}\n")
    threading.Thread(target=_open_browser, daemon=True).start()
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=False)
