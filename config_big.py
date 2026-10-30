# Based on your 3 pyramids:
# 1-100 image: cyan=doomed, yellow=45°, green=hex
# 1-324 image: shows fat belly = waste grows, need 500k+ steps at bottom
# 941-1000 screenshot: L=31/32 bug = we must go BELOW ceil(sqrt(n))
START_N = 10
END_N = 1000
TOTAL_STEPS = 500000  # bottom of pyramid needs more, your 350k not enough for 941+
DRAW_EVERY = 25000
START_TEMP = 0.40
END_TEMP = 0.00003
COOL_RATE = 0.999988
BASE_MOVE_SIZE = 0.06  # smaller for dense packing at n=300+
BASE_ANGLE_SIZE = 0.35  # allow full cyan rotation from your n=10 image
BEST_FOLDER = "best_results_v4"
PIC_SIZE = 512

# RED diagonal from your images: 1,4,9,16,25,36,49,64,81,100,121,144,169,196,225,256,289,324,361,400,441,484,529,576,625,676,729,784,841,900,961,1024
PERFECT_SQUARES = {k*k for k in range(1,33)}

# From your Deckard pyramid colors (read manually from your screenshots):
YELLOW_45 = {5,8,10,18,29,45,68,88,89,102,103,111,112,128,145,146,166,186,187,207,228,229,251,273,274,298}
GREEN_HEX = {41,68,71,72,73,74,75,76,79,86,87,90,91,106,107,108,115,130,131,152,153,172,173,174,193,194,195,216,217,238,239,240,262,263,264,286,287,288}
CYAN_DOOMED = {10,11,12,13,14,15,17,19,20,21,22,23,24,26,27,28,30,31,32,33,34,35,37,38,39,40,42,43,44,46,47,48,50,51,52,53,54,55,56,57,58,59,60,61,62,63,65,66,67,69,70,77,78,80,82,83,84,85,92,93,94,95,96,97,98,99,101,104,105,109,110,113,114,116,117,118,119,120}
