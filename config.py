# ======# === config.py ====
# settings you change most often

START_N = 1
END_N   = 20              # change per batch on phone

TOTAL_STEPS = 80000
DRAW_EVERY  = 20000       # 0 = only final picture

START_TEMP = 0.18
END_TEMP   = 0.0003
COOL_RATE  = 0.99997

BASE_MOVE_SIZE  = 0.06
BASE_ANGLE_SIZE = 0.04

BEST_FOLDER = "best_results"
PIC_SIZE    = 512
BRANCH_NAME = "lightweight+v4-fixed"