import json, os, csv, time, math, hashlib, glob
BEST_FOLDER = "best_results_v4"
HISTORY_FILE = "history_v4.csv"
os.makedirs(BEST_FOLDER, exist_ok=True)

def get_code_hash():
    try:
        with open("main.py","rb") as f: return hashlib.sha256(f.read()).hexdigest()[:8]
    except: return "nohash"

def log_history(n, step, L, extra=""):
    exists = os.path.exists(HISTORY_FILE)
    with open(HISTORY_FILE, "a", newline="") as f:
        w = csv.writer(f)
        if not exists:
            w.writerow(["timestamp","n","step","L","score","code_hash","branch","note"])
        score = L / math.sqrt(n) - 1 if n>0 else 0
        w.writerow([time.strftime("%Y-%m-%d %H:%M:%S"), n, step, f"{L:.6f}", f"{score:.6f}", get_code_hash(), "v4-real", extra])

def save_best_result(n, L, squares):
    path = f"{BEST_FOLDER}/best_n{n}.json"
    data = {"n": n, "L": float(L), "squares": squares, "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "branch": "v4-real", "source_pyramid": "Deckard 1-324 image"}
    with open(path, "w") as f: json.dump(data, f, indent=2)

def get_best_L(n):
    path = f"{BEST_FOLDER}/best_n{n}.json"
    if not os.path.exists(path): return float("inf")
    with open(path, "r") as f: return json.load(f)["L"]

def make_submission_csv(output="submission_v4.csv"):
    files = glob.glob(f"{BEST_FOLDER}/best_n*.json")
    if not files: print("No results!"); return
    all_data=[]
    for file in files:
        with open(file,"r") as f: all_data.append(json.load(f))
    all_data.sort(key=lambda d: d["n"])
    row_id=0
    with open(output,"w",newline="") as f:
        w=csv.writer(f)
        w.writerow(["id","n","square_id","x","y","angle"])
        for d in all_data:
            for sq_id,sq in enumerate(d["squares"]):
                w.writerow([row_id, d["n"], sq_id, f"{sq['x']:.6f}", f"{sq['y']:.6f}", f"{sq.get('angle',0):.6f}"])
                row_id+=1
    total=sum(d["L"]/math.sqrt(d["n"])-1 for d in all_data)
    print(f"[v4-real] {output} rows={row_id} total_score={total:.6f} avg={(total/len(all_data)):.6f}")
