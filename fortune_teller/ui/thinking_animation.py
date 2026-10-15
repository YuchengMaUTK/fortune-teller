"""Compatibility wrapper around the shared Rich status."""
from .animation import LoadingAnimation


class ChatThinkingAnimation(LoadingAnimation):
    def __init__(self, prefix=None):
        super().__init__("霄占正在思考…")
