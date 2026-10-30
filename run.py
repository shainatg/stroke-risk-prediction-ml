import sys
import os
from src import config
from app import app

if __name__ == "__main__":
    port = config.PORT
    print("=" * 70)
    print("  STROKE RISK PREDICTION USING MACHINE LEARNING")
    print("  Health Informatics Postgraduate Demonstration Suite")
    print("=" * 70)
    print(f"  * Server URL: http://127.0.0.1:{port}")
    print(f"  * Environment: {'Debug' if config.DEBUG else 'Production'}")
    print(f"  * Dataset: {config.DATA_PATH}")
    print(f"  * Best Model: {config.BEST_MODEL_PATH}")
    print("=" * 70)
    print("  Press Ctrl+C to terminate the server.\n")

    app.run(host="127.0.0.1", port=port, debug=config.DEBUG)
