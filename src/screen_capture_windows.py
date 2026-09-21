import mss
import mss.tools

output_path = r"\\wsl.localhost\Ubuntu\home\devel\prototype\design_intelligence\src\windows_screen.png"

with mss.mss() as screen:
    monitor = screen.monitors[1]
    screenshot = screen.grab(monitor)

    mss.tools.to_png(
        screenshot.rgb,
        screenshot.size,
        output=output_path
    )

print(output_path)