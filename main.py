from fastapi import FastAPI
from routes import router
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request

app = FastAPI()

app.include_router(router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    print(exc.errors())

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Data inválida. Use o formato AAAA-MM-DD."
        }
    )