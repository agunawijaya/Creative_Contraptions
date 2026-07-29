import struct
from collections import OrderedDict
data = open(r'C:\Projects\Creative_Contraptions\work\CONTRAP', 'rb').read()
print('CONTRAP size', len(data))
c = OrderedDict()
for i in range(36):
    off = i * 6
    idv, offset = struct.unpack_from('<HI', data, off)
    if idv == 0:
        print('  [%d] id=0 (end of directory)' % i)
        break
    c.setdefault(idv, []).append(offset)
print()
print('goal id -> #variants (starting screens):')
for g, offs in c.items():
    print('  goal %d : %d variant(s)  offsets=%s' % (g, len(offs), offs))
print()
print('TOTAL directory entries used:', sum(len(v) for v in c.values()))
