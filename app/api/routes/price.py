from fastapi import APIRouter
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from app.services.price_feed import PriceFeed
import json

price_feed = PriceFeed(max_seconds=15.0, tick_ms=500)

router = APIRouter(prefix="/price", tags=["price"])


@router.on_event("startup")
async def _start_feed():
    await price_feed.start()

@router.on_event("shutdown")
async def _stop_feed():
    await price_feed.stop()
    
@router.get("/latest")
async def get_latest():
    snap = await price_feed.latest()
    if not snap:
        return JSONResponse({"status": "warming_up"}, status_code=503)
    return {"price": snap["price"], "ts": snap["ts"], "age_ms": snap["age_ms"]}

@router.get("/recent")
async def get_recent():
    return await price_feed.recent()

@router.websocket("/ws/price")
async def ws_price(ws: WebSocket):
    await ws.accept()
    q = await price_feed.subscribe()
    try:
        while True:
            snap = await q.get()
            await ws.send_text(json.dumps(snap))
    except WebSocketDisconnect:
        await price_feed.unsubscribe(q)