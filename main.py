import atexit
from server import mcp, cleanup

if __name__ == "__main__":
    mcp.run()

atexit.register(cleanup)