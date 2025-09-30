import numpy as np

class Test:
    a = np.array([[2, 2, 0, 0], [8, 0, 32, 64], [128, 2, 0, 4], [8, 0, 16, 64]])
    rand_ix = np.random.choice(max(a.shape), 2)
    print(rand_ix)
