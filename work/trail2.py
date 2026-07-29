import os, glob
from PIL import Image
import colorsys
F = r"C:\Projects\Creative_Contraptions\work\frames"
files = sorted(glob.glob(os.path.join(F, "f*.png")))
imgs = [Image.open(f).convert("RGB") for f in files]
W, H = imgs[0].size
# motion = beda antar frame berturut-turut
print("perbedaan antar-frame (jumlah piksel berubah, bbox):")
base = imgs[5].load()  # latar stabil
trail = Image.new("RGB", (W, H))
tp = trail.load()
for y in range(H):
    for x in range(W):
        r, g, b = base[x, y]; tp[x, y] = (r//4, g//4, b//4)
for i in range(1, len(imgs)):
    a = imgs[i-1].load(); b = imgs[i].load()
    xs=[]; ys=[]
    for y in range(H):
        for x in range(W):
            if a[x,y]!=b[x,y]:
                xs.append(x); ys.append(y)
    if xs:
        print("  f%03d->%03d: %d px  bbox x[%d..%d] y[%d..%d]"%(i-1,i,len(xs),min(xs),max(xs),min(ys),max(ys)))
        hue=i/len(imgs); cr,cg,cb=[int(c*255) for c in colorsys.hsv_to_rgb(hue*0.85,1,1)]
        for x,y in zip(xs,ys): tp[x,y]=(cr,cg,cb)
trail.resize((W*2,H*2), Image.NEAREST).save(os.path.join(F,"..","trail2.png"))
print("-> trail2.png")
