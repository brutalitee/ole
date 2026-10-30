# ======# === config.py ====
# settings you change most often

START_N = 1
END_N   = 50          # inclusive. Change for each batch (1-50, 51-100, ...)

TOTAL_STEPS = 80000   # lower = faster, higher = better (try 40000–150000)
DRAW_EVERY  = 0       # 0 = never draw (recommended on phone)

START_TEMP = 0.15
END_TEMP   = 0.0005
COOL_RATE  = 0.99997

BASE_MOVE_SIZE  = 0.05
BASE_ANGLE_SIZE = 0.04

BEST_FOLDER = "best_results"