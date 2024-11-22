import sys

import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

path = sys.argv[1]

key = np.load("key.npy")
traces = np.load(path + "/em_aligned.npy")
plains = np.load(path + "/plain_aligned.npy")

nr_traces = traces.shape[0]
nr_points = traces.shape[1]

corrs = np.zeros((256,nr_points))

for j in tqdm(range(0, nr_points)):
    # compute correlation for 0-th key byte
    # an attacker would have to try out all possible
    # 256 byte values and chose the one with the highest
    # correlation
    xors = np.array([ plains[k, 0]^key[0] for k in range(0, nr_traces) ])
    c = np.corrcoef(traces[:, j], xors)[0][1]
    corrs[key[0],j] = c

plt.figure()
plt.plot(corrs[key[0], :])
plt.show()
