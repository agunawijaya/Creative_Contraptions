import json
draws = json.load(open(r'C:\Projects\Creative_Contraptions\port\cc\draws\draws_goal1.json'))
anim = json.load(open(r'C:\Projects\Creative_Contraptions\work\emu_caps\anim_goal1.json'))
frames = sorted(set(a['frame'] for a in anim))
print('anim frames head:', frames[:12], 'total', len(frames), 'entries', len(anim))
print('draws_goal1 entries:', len(draws))
dd = [(d['arch'], d['idx'], d['x'], d['y']) for d in draws]
f0 = frames[0]
a0 = [(a['arch'], a['idx'], a['x'], a['y']) for a in anim if a['frame'] == f0]
print('anim frame', f0, 'count', len(a0))
print('draws == anim-frame0 set?', set(dd) == set(a0))
print('in draws not in f0:', [x for x in dd if x not in a0][:20])
print('in f0 not in draws:', [x for x in a0 if x not in dd][:20])
