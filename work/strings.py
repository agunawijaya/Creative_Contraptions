"""Ekstrak string ASCII dari CONTRAP.EXE hasil unpack."""
import re

f = r"C:\Projects\Creative_Contraptions\work\unpack\CONTRAP_UNPACKED.EXE"
b = open(f, "rb").read()

# runs printable >= 4 char
strs = []
for m in re.finditer(rb"[\x20-\x7e]{4,}", b):
    s = m.group().decode("ascii")
    strs.append((m.start(), s))

print("Total string (>=4 char): %d\n" % len(strs))
print("=== SEMUA STRING (offset : teks) ===")
for off, s in strs:
    print("%06X  %s" % (off, s))
