import subprocess

def get_system_volume():
    """Return current macOS system volume (0-100)"""
    result = subprocess.run(
        ["osascript", "-e", "output volume of (get volume settings)"],
        capture_output=True,
        text=True
    )
    try:
        return int(result.stdout.strip())
    except:
        return 50  # fallback
