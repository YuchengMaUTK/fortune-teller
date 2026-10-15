"""Rich loading status; quiet and escape-free when output is redirected."""
from rich.text import Text
from .rendering import get_console


class LoadingAnimation:
    def __init__(self, message: str = "处理中"):
        self.message = message
        self.status = None

    def start(self) -> None:
        if self.status is not None:
            return
        console = get_console()
        if console.is_terminal:
            self.status = console.status(Text(self.message), spinner="dots", refresh_per_second=10)
            self.status.start()
        else:
            console.print(Text(self.message, style="muted"))

    def stop(self) -> None:
        if self.status is not None:
            self.status.stop()
            self.status = None
