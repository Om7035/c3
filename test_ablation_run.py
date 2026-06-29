#!/usr/bin/env python
"""Direct test of ablation.py main() with file-based output."""
import sys
import os
from dotenv import load_dotenv

# Write to file so we can see output
log_file = open("E:/C³/ablation_test_output.txt", "w", buffering=1)

def log(msg):
    print(msg, file=log_file, flush=True)
    print(msg)

try:
    log("=== Starting ablation test ===")
    load_dotenv()
    log(f"Env loaded. Backend: {os.environ.get('C3_BACKEND')}")

    import asyncio
    log("Asyncio imported")

    # Import ablation
    sys.path.insert(0, os.path.abspath('.'))
    from benchmarks.ablation import main, load_suite
    log("Ablation module imported")

    # Test load_suite
    suite = load_suite()
    log(f"Loaded {len(suite)} questions")

    # Run main
    log("Starting main() async run...")
    asyncio.run(main())
    log("=== Ablation completed ===")

except Exception as e:
    import traceback
    log(f"ERROR: {e}")
    log(traceback.format_exc())
finally:
    log_file.close()
