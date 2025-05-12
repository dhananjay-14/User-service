import json
from typing import Any, Dict, List, Union
from fastapi import WebSocket

class Subscription:
    """Holds a WebSocket and its filter criteria."""
    def __init__(self, ws: WebSocket, by_id: int = None, search: Dict[str, Any] = None):
        self.ws = ws
        self.by_id = by_id
        self.search = search

class ConnectionManager:
    """Manages WebSocket connections and subscriptions for user events."""
    def __init__(self):
        # List to store active WebSocket subscriptions
        self.active: List[Subscription] = []

    async def connect(self, ws: WebSocket):
        # Accept new WebSocket connection and add to active subscriptions
        await ws.accept()
        self.active.append(Subscription(ws))

    def disconnect(self, ws: WebSocket):
        # Remove WebSocket from active subscriptions
        self.active = [s for s in self.active if s.ws != ws]

    def subscribe_to_id(self, ws: WebSocket, user_id: int):
        # Subscribe WebSocket to specific user ID
        for s in self.active:
            if s.ws == ws:
                s.by_id = user_id

    def subscribe_to_search(self, ws: WebSocket, filters: Dict[str, Any]):
        # Subscribe WebSocket to search filters
        for s in self.active:
            if s.ws == ws:
                s.search = filters

    async def broadcast_event(self, event: Dict[str, Any]):
        """
        Broadcast user events to relevant subscribers.
        event = {
          "type": "created" | "updated" | "deleted",
          "user": { ... }  # full user payload
        }
        """
        for sub in list(self.active):
            try:
                match = False

                # Check for ID-based subscription match
                if sub.by_id is not None and event["user"]["id"] == sub.by_id:
                    match = True

                # Check for search-based subscription match
                if sub.search is not None:
                    # Verify all filters match the event data (case-insensitive)
                    match = all(
                        str(event["user"].get(k, "")).lower().find(str(v).lower()) >= 0
                        for k, v in sub.search.items()
                    )

                # Send event to matching subscribers
                if match:
                    await sub.ws.send_text(json.dumps(event))
            except:
                # Clean up failed connections
                self.disconnect(sub.ws)

manager = ConnectionManager()
