import os
import sys

# Ensure the repository root (which contains the BioSUR package) is importable
# regardless of where pytest is invoked from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
