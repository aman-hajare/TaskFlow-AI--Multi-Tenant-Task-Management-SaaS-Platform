import asyncio
from typing import Callable, Dict, List
from app.utils.logger import logger


class EventBus:

    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):

        if event_type not in self.subscribers:
            self.subscribers[event_type] = []

        self.subscribers[event_type].append(handler)

        logger.info(f"Subscribed handler {handler.__name__} to event {event_type}")

    async def publish(self, event_type: str, data: dict):

        handlers = self.subscribers.get(event_type, [])

        if not handlers:
            return

        tasks = []

        for handler in handlers:
            tasks.append(self._safe_execute(handler, data))

        await asyncio.gather(*tasks)

    async def _safe_execute(self, handler: Callable, data: dict):

        try:
            await handler(data)

        except Exception as e:
            logger.error(
                f"Event handler {handler.__name__} failed: {str(e)}"
            )


event_bus = EventBus()