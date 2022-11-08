import random
import plotly.graph_objects as go

def make_figure(P, W, L, H):
    random.seed(42) # consistent colors
    cubes = [ ]

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