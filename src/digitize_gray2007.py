"""Digitize Gray, Gray & Wegner (2007) Fig. 1 into data/gray2007_digitized.csv.

Usage: python src/digitize_gray2007.py <figure.png>. The pixel constants below fit one extraction of the published
figure (axes at x 62.5-527.5, y 488.5-11.5); a different extraction needs new constants. The figure is not
included here. Character positions are box centres and ink centroids, rescaled to 0-1."""
import sys
import numpy as np
from PIL import Image
im = np.array(Image.open(sys.argv[1]).convert('L')).astype(float)
X0,X1,Y0,Y1 = 62.5, 527.5, 488.5, 11.5
boxes = {  # name: (xmin,xmax,ymin,ymax) from connected-component pass (k=1)
 'baby':(148,186,23,57),'girl':(322,367,36,76),'chimp':(196,239,57,95),'woman':(462,505,66,113),
 'dog':(175,214,94,134),'you':(470,513,113,146),'man':(426,465,109,154),'frog':(76,118,163,200),
 'PVS man':(152,189,219,262),'fetus':(75,115,224,259),'dead woman':(187,224,374,412),
 'God':(473,509,428,467),'robot':(267,302,423,475)}
rows=[]
for n,(a,b,c,d) in boxes.items():
    w = 255-im[c:d+1,a:b+1]; ys,xs=np.mgrid[c:d+1,a:b+1]
    cx=(w*xs).sum()/w.sum(); cy=(w*ys).sum()/w.sum()
    bx=(a+b)/2; by=(c+d)/2
    A=(bx-X0)/(X1-X0); E=(Y0-by)/(Y0-Y1); Ac=(cx-X0)/(X1-X0); Ec=(Y0-cy)/(Y0-Y1)
    rows.append((n,A,E,Ac,Ec))
Amin=min(r[1] for r in rows); Amax=max(r[1] for r in rows); Emin=min(r[2] for r in rows); Emax=max(r[2] for r in rows)
print(f"{'char':12s} A_box E_box | A_ink E_ink | A_rescaled E_rescaled")
for n,A,E,Ac,Ec in sorted(rows,key=lambda r:-r[2]):
    print(f"{n:12s} {A:.2f}  {E:.2f}  | {Ac:.2f}  {Ec:.2f}  | {(A-Amin)/(Amax-Amin):.2f}  {(E-Emin)/(Emax-Emin):.2f}")
