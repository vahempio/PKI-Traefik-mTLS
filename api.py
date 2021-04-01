from typing import Optional
from fastapi import FastAPI, Header
from urllib import parse

app = FastAPI()

@app.get("/")
async def root(x_forwarded_tls_client_cert_info: Optional[str] = Header(None)):
    cert_info = parse.unquote_plus(x_forwarded_tls_client_cert_info)
    return cert_info
