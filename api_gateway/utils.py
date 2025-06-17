from fastapi import HTTPException
import httpx


def unwrap_httpx_error(e: httpx.HTTPStatusError):
    # Попробуем распарсить JSON
    try:
        payload = e.response.json()
    except ValueError:
        # если не JSON — возьмём текст
        message = e.response.text or str(e)
    else:
        # если в нём есть ключ "detail", берем его, иначе сам payload
        message = payload.get("detail", payload)
    return HTTPException(status_code=e.response.status_code, detail=message)
