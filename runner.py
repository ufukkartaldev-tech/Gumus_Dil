import sys
import os
import traceback

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from src.ide.main import main
    main()
except Exception:
    with open("crash_log.txt", "w", encoding="utf-8") as f:
        f.write(traceback.format_exc())
    print("CRASHED! Check crash_log.txt")
