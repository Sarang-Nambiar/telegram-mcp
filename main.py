import atexit
from server import mcp
from tools.telegram_tools import cleanup

if __name__ == "__main__":
    mcp.run()

atexit.register(cleanup)