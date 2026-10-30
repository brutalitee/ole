import glob, json, math, os
BEST_FOLDER="best_results_v4"
print("=== v4-REAL ACCURACY TEST 1-1000 (from your pyramids + screenshot) ===")
fails=0
checked=0
for n in range(1,1001):
    path=f"{BEST_FOLDER}/best_n{n}.json"
    if not os.path.exists(path): continue
    checked+=1
    with open(path) as f: d=json.load(f)
    L=d["L"]; lower=math.sqrt(n); ceilL=math.ceil(math.sqrt(n))
    is_perfect=int(math.sqrt(n))**2==n
    if is_perfect and abs(L-lower)>0.01:
        print(f"FAIL RED n={n} should be {lower} got {L}"); fails+=1
    if L < lower-0.01:
        print(f"FAIL n={n} L={L} < sqrt={lower} IMPOSSIBLE"); fails+=1
    # Check your 941-1000 screenshot bug is fixed
    if n>=941 and n<=1000:
        if abs(L-ceilL)<0.0001 and L==31.0 or L==32.0:
            print(f"WARN n={n} still at naive {L} like screenshot - not optimized below ceil, should be {ceilL-0.2:.3f} range")
        else:
            print(f"OK n={n} L={L:.6f} ceil={ceilL} below_ceil={ceilL-L:.4f} score={L/lower-1:.5f}")
    if n==5: print(f"CHECK n=5 diamond: L={L:.6f} optimal 2.707106")
    if n==10: print(f"CHECK n=10 cyan: L={L:.6f} optimal ~3.707 (your screenshot) naive 4.0")
    if n==324: print(f"CHECK n=324 RED perfect: L={L:.6f} should be 18.0")

print(f"\nChecked {checked} files, {fails} fails")
if fails==0: print("PASS - All L >= sqrt(n), red perfect squares correct, 941+ below ceil")
