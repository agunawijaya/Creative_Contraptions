import json
a = json.load(open(r'C:\Projects\Creative_Contraptions\work\emu_caps\anim_goal128.json'))
fs = sorted(set(x['frame'] for x in a))
print('frames', len(fs), fs[:24])
print('entries', len(a))
byf = {}
for x in a:
    byf.setdefault(x['frame'], []).append((x['arch'], x['idx'], x['x'], x['y']))
for f in fs[:6]:
    print('frame', f, ':', byf[f])
