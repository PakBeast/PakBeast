"""Main entry point for the PakBeast application."""

import sys
from pathlib import Path

# Add pakbeast directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from core.app import main

if __name__ == "__main__":
    main()

