import random, math, time
from config import *
from best_manager import save_best_result, get_best_L, log_history
try:
    from config_big import YELLOW_45, GREEN_HEX, CYAN_DOOMED, PERFECT_SQUARES
except:
    YELLOW_45=set(); GREEN_HEX=set(); CYAN_DOOMED=set(); PERFECT_SQUARES={k*k for k in range(1,33)}

def rotated_bbox_size(angle):
    return abs(math.cos(angle)) + abs(math.sin(angle))

def compute_L(squares):
    min_x=float('inf'); max_x=-float('inf'); min_y=float('inf'); max_y=-float('inf')
    for s in squares:
        w=rotated_bbox_size(s.get("angle",0))
        min_x=min(min_x, s["x"]); max_x=max(max_x, s["x"]+w)
        min_y=min(min_y, s["y"]); max_y=max(max_y, s["y"]+w)
    return max(max_x-min_x, max_y-min_y)

def get_corners(s):
    angle=s.get("angle",0); w=rotated_bbox_size(angle)
    cx=s["x"]+w/2; cy=s["y"]+w/2
    pts=[(-0.5,-0.5),(0.5,-0.5),(0.5,0.5),(-0.5,0.5)]
    ca=math.cos(angle); sa=math.sin(angle)
    corners=[]
    for px,py in pts:
        rx=px*ca - py*sa + cx
        ry=px*sa + py*ca + cy
        corners.append((rx,ry))
    return corners

def check_overlap(s1,s2):
    polys=[get_corners(s1), get_corners(s2)]
    for poly in polys:
        for i in range(4):
            x1,y1=poly[i]; x2,y2=poly[(i+1)%4]
            nx,ny=-(y2-y1), x2-x1
            if nx==0 and ny==0: continue
            def proj(p): return [x*nx + y*ny for x,y in p]
            p1=proj(polys[0]); p2=proj(polys[1])
            if max(p1) < min(p2)-1e-9 or max(p2) < min(p1)-1e-9:
                return False
    return True

def random_packing(n):
    side=math.ceil(math.sqrt(n))
    squares=[]
    # RED - perfect squares from your red diagonal
    if int(math.sqrt(n))**2 == n:
        k=int(math.sqrt(n))
        for i in range(n):
            squares.append({"x": float(i%k), "y": float(i//k), "angle": 0.0})
        return squares
    # GREEN - hex packing (brick) from your green cells
    use_hex = n in GREEN_HEX
    for i in range(n):
        row=i//side; col=i%side
        x=col*1.01 + (0.5 if use_hex and row%2==1 else 0) + random.uniform(-0.05,0.05)
        y=row*1.01 + random.uniform(-0.05,0.05)
        ang=0.0
        # YELLOW - 45 deg diamond from your n=5 image
        if n in YELLOW_45 and i==n-1:
            ang=0.78539816339
            x=side/2-0.707; y=side/2-0.707
        # CYAN - your n=10 screenshot - free rotation
        elif n>=10 and (n in CYAN_DOOMED or BASE_ANGLE_SIZE>0):
            # for 941-1000, use smaller random to go below ceil
            if n>=900:
                ang=random.uniform(-0.15,0.15)
            else:
                ang=random.uniform(-BASE_ANGLE_SIZE, BASE_ANGLE_SIZE)
        squares.append({"x": x, "y": y, "angle": ang})
    return squares

print(f"=== v4-REAL START {START_N}->{END_N} | BASED ON PYRAMID IMAGES ===")
for n in range(START_N, END_N+1):
    best_L=get_best_L(n)
    squares=random_packing(n)
    L=compute_L(squares)
    lower=math.sqrt(n)
    if L < lower-0.01:
        print(f"SKIP INVALID n={n} L={L} < sqrt")
        continue
    # For large n, log if we are stuck at ceil like your screenshot
    ceil_L=math.ceil(math.sqrt(n))
    if L >= ceil_L-0.0001 and L <= ceil_L+0.0001 and n>=941:
        print(f"WARNING n={n} at naive ceil {ceil_L} like your screenshot - will try to go below")
    
    print(f"\nn={n} start L={L:.5f} best={best_L:.5f} lower={lower:.3f} ceil={ceil_L} cat={'RED' if n in PERFECT_SQUARES else 'YELLOW' if n in YELLOW_45 else 'GREEN' if n in GREEN_HEX else 'CYAN' if n in CYAN_DOOMED else 'ORANGE'}")
    temp=START_TEMP
    for step in range(1, TOTAL_STEPS+1):
        idx=random.randrange(n)
        old=squares[idx].copy()
        # for 941-1000 use tiny moves to squeeze below ceil
        move = BASE_MOVE_SIZE * (0.5 if n>=900 else 1.0)
        squares[idx]["x"]+=random.uniform(-move, move)
        squares[idx]["y"]+=random.uniform(-move, move)
        if BASE_ANGLE_SIZE>0:
            squares[idx]["angle"]+=random.uniform(-0.03,0.03)
        new_L=compute_L(squares)
        overlap=False
        # check only nearby to speed up for large n
        for j in range(n):
            if j==idx: continue
            # quick AABB reject
            if abs(squares[idx]["x"]-squares[j]["x"])>2 or abs(squares[idx]["y"]-squares[j]["y"])>2:
                continue
            if check_overlap(squares[idx], squares[j]):
                overlap=True; break
        accept=False
        if not overlap and new_L >= lower-0.001:
            if new_L < L or random.random() < math.exp(-(new_L-L)/max(temp,1e-6)):
                accept=True
        if accept:
            L=new_L
            if L < best_L:
                best_L=L
                export=[{"x": float(s["x"]), "y": float(s["y"]), "angle": float(s["angle"])} for s in squares]
                save_best_result(n, L, export)
                note="BELOW_CEIL" if L < math.ceil(math.sqrt(n))-0.001 else ""
                log_history(n, step, L, note)
                print(f"  -> NEW BEST n={n} L={L:.6f} {note} score={L/math.sqrt(n)-1:.5f} step={step}")
        else:
            squares[idx]=old
        temp=max(END_TEMP, temp*COOL_RATE)
        if step % DRAW_EVERY ==0:
            print(f"    step {step} L={L:.6f} score={L/math.sqrt(n)-1:.6f} temp={temp:.5f}")
    print(f"  done n={n} final L={L:.6f} best {best_L:.6f}")
