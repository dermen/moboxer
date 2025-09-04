import os
import sys
import random
import time


jiggle_script = sys.argv[1]
pdbin = sys.argv[2]
pdbout = sys.argv[3]
seed = int(time.time() * 1000) + os.getpid()
shift_min, shift_max = 0.4,4
random.seed(seed)
#seed = random.getrandbits(16)
shift = random.uniform(shift_min, shift_max)

cmd=f"""awk -f {jiggle_script} \
 -v shift=byB -v seed={int(seed)} \
 -v shift={shift:.2f} \
 -v frac_thrubond=0.9 -v ncyc_thrubond=500 \
 -v frac_magnforce=1.1 -v ncyc_magnforce=500 \
 -v shift_scale=1 \
 -v dry_shift_scale=1 {pdbin} > {pdbout}
"""
print(cmd)

os.system(cmd)

