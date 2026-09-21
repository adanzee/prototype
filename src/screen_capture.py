import os
from datetime import datetime
import mss


def capture_screen():

    os.makedirs("screenshots", exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    file_path = f"screenshots/screen_{timestamp}.png"

    with mss.mss() as screen:

        monitor = screen.monitors[1]

        screenshot = screen.grab(monitor)

        mss.tools.to_png(
            screenshot.rgb,
            screenshot.size,
            output=file_path
        )

    return file_path