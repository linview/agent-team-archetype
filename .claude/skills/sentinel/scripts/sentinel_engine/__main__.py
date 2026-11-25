"""python -m sentinel_engine 入口(等价 cli.main)。"""
import sys
from sentinel_engine.cli import main

if __name__ == "__main__":
    sys.exit(main())
