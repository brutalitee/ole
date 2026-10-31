# ============================================================
# COMPLETE FIXED VERSION - Square Packing for Kaggle
# Lightweight + Multi-start + Resume + Robust Geometry
# Pure-Python PNG (no matplotlib)
# ============================================================

# ----------------------------------------------------------------
# FILE: config.py
# ----------------------------------------------------------------
BRANCH_NAME = "fixed-robust-v1"

START_N = 1
END_N = 15                 # change this range as needed

TOTAL_STEPS = 80000        # per start
NUM_STARTS = 3             # multi-start
DRAW_EVERY = 20000

START_TEMP = 0.25
END_TEMP = 0.0005
COOL_RATE = 0.99997

BASE_MOVE_SIZE = 0.05
BASE_ANGLE_SIZE = 0.12

BEST_FOLDER = "best_results"
PIC_SIZE = 400