# app/price_feed.py
import asyncio, time, json
from collections import deque
from typing import Deque, Dict, Any, Set
import httpx

class PriceFeed:
    def __init__(self, *, max_seconds: float = 15.0, tick_ms: int = 500):
        # ~2 Hz ring buffer
        self.tick_ms = tick_ms
        self.interval = tick_ms / 1000.0
        self.capacity = max(1, int(max_seconds / self.interval))
        self.buffer: Deque[Dict[str, Any]] = deque(maxlen=self.capacity)

        self._task: asyncio.Task | None = None
        self._subscribers: Set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()
        self._client = httpx.AsyncClient(timeout=1.0)
        self._running = asyncio.Event()

    async def start(self):
        if self._task is None:
            self._running.set()
            self._task = asyncio.create_task(self._run())

    async def stop(self):
        self._running.clear()
        if self._task:
            await self._task
            self._task = None
        await self._client.aclose()

    async def _fetch_price(self) -> Dict[str, Any]:
        # Kraken ticker endpoint example; adapt to your existing price_getter
        # BTC/USD pair symbol may vary in Kraken (e.g., XBTUSD). Keep your working one.
        r = await self._client.get("https://api.kraken.com/0/public/Ticker?pair=XBTUSD")
        data = r.json()
        # Extract last trade/close price (Kraken returns string lists)
        last = float(data["result"]["XXBTZUSD"]["c"][0])
        now = time.time()
        return {"ts": now, "price": last, "source": "kraken", "age_ms": self.tick_ms}

    async def _run(self):
        backoff = self.interval
        while self._running.is_set():
            try:
                snap = await self._fetch_price()
                async with self._lock:
                    self.buffer.append(snap)
                # broadcast non-blocking
                for q in list(self._subscribers):
                    if q.full():
                        # drop oldest to avoid buildup
                        try: q.get_nowait()
                        except: pass
                    await q.put(snap)
                backoff = self.interval  # reset after success
            except Exception as e:
                # on error, wait a bit longer (simple backoff)
                backoff = min(backoff * 2, 5.0)
            await asyncio.sleep(backoff)

    async def latest(self) -> Dict[str, Any] | None:
        async with self._lock:
            if not self.buffer:
                return None
            snap = self.buffer[-1]
        age_ms = int((time.time() - snap["ts"]) * 1000)
        return {**snap, "age_ms": age_ms}

    async def recent(self) -> list[Dict[str, Any]]:
        async with self._lock:
            return list(self.buffer)

    # --- subscriptions for WS/SSE ---
    async def subscribe(self, max_queue: int = 5) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue(maxsize=max_queue)
        self._subscribers.add(q)
        # push current latest immediately if we have one
        latest = await self.latest()
        if latest:
            await q.put(latest)
        return q

    async def unsubscribe(self, q: asyncio.Queue):
        self._subscribers.discard(q)
