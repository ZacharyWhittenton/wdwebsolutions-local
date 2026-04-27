import os

import uvicorn


HOST = os.environ.get("CONTACT_API_HOST", "127.0.0.1")
PORT = int(os.environ.get("CONTACT_API_PORT", "8000"))
RELOAD = os.environ.get("CONTACT_API_RELOAD", "").lower() == "true"


if __name__ == "__main__":
    os.environ.setdefault("ENVIRONMENT_CONFIG", "local.config.json")
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
