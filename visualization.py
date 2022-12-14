import random
import plotly.graph_objects as go
from matplotlib import pyplot as plt
import numpy as np

def make_figure(P, points, W, L, H):
    random.seed(42) # consistent colors
    cubes = [ ]

    px, py, pz = [ ], [ ], [ ]
    for p in points:
        px.append(p[0])
        py.append(p[1])
        pz.append(p[2])

    scatter = go.Scatter3d(x=px, y=py, z=pz,
                 mode='markers',
                 marker=dict(size=5)
                 )

    cubes.append(scatter)

    for p in P:
        pxw = p.x + p.w
        pyl = p.y + p.l
        pzh = p.z + p.h
        cx = [p.x, p.x, pxw, pxw, p.x, p.x, pxw, pxw]
        cy = [p.y, pyl, pyl, p.y, p.y, pyl, pyl, p.y]
        cz = [p.z, p.z, p.z, p.z, pzh, pzh, pzh, pzh]
        i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
        j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
        k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

        cp = go.Mesh3d(x=cx, y=cy, z=cz, i=i, j=j, k=k,
                       color="rgb"+str((random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))),
                       opacity=0.70,
                       flatshading=True)

        cubes.append(cp)

    fig = go.Figure(data=cubes)

    fig.update_layout(
        scene=dict(
            xaxis=dict(range=[-10, W + 10], ),
            yaxis=dict(range=[-10, L + 10], ),
            zaxis=dict(range=[-10, H + 1000], ),
        )
    )
    fig.show()

def make_histo(P, name):
    VP = [ p.w * p.l * p.h for p in P ]
    SP = [ max(p.w, p.l, p.h) for p in P ]

    # Creating histogram
    fig, ax = plt.subplots()
    ax.hist(np.array(VP), bins=len(P))
    plt.savefig("out/volume_" + name + ".pdf")
    fig.clear()

    fig, ax = plt.subplots()
    ax.hist(np.array(SP), bins=len(P))
    plt.savefig("out/sidelength_" + name + ".pdf")
    fig.clear()