import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import post_to_all

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title="Automated Multi-Platform Posting System", version="1.0.0")


@app.exception_handler(RequestValidationError)
async def validation_handler(_: Request, exc: RequestValidationError):
    errors = [{
        "field": ".".join(str(p) for p in e["loc"] if p != "body") or "body",
        "message": str(e["msg"]).removeprefix("Value error, "),
    } for e in exc.errors()]
    return JSONResponse(status_code=422, content={"success": False, "errors": errors})


@app.post("/posting", response_model=PostingResponse, tags=["posting"])
async def posting(req: PostingRequest) -> PostingResponse:
    """Publish the message to every configured platform. `success` is true if at least one platform succeeded."""
    results = await post_to_all(req.message, req.link)
    return PostingResponse(success=any(r.status == "success" for r in results), results=results)
