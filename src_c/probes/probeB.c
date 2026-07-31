/* probeB.c — apa yang menentukan URUTAN RANTAI PERBANDINGAN `switch`?
 *
 * Gejala (main_ 0x05f1):
 *   KITA  cmp ax,3 / jne / jmp L   lalu  cmp ax,2 / jne / jmp L
 *   ASLI  cmp ax,2 / jne / jmp L   lalu  cmp ax,3 / jne / jmp L
 * Sumbernya `switch (mode) { case 3: ...; case 2: ...; }` — dan menukar urutan
 * `case` DITOLAK (badan harus tetap case 3 dulu). Jadi urutan BADAN dan urutan
 * RANTAI tidak bergerak bersama; yang dicari: apa yang memisahkan keduanya.
 *
 * Yang dicari di keluaran: untuk tiap fungsi, urutan konstanta di `cmp ax,K`.
 */

extern int m;
extern int f1(), f2(), f3();

/* B1 — persis bentuk main_: case 3 lalu case 2, badan ber-`continue`. */
pb1(n)
int n;
{
    int i;
    for (i = 0; i < n; i++) {
        switch (m) {
        case 3:
            if (f1() == -1)
                continue;
            break;
        case 2:
            if (f2() == -1)
                continue;
            break;
        }
        f3();
    }
}

/* B2 — urutan case DIBALIK. */
pb2(n)
int n;
{
    int i;
    for (i = 0; i < n; i++) {
        switch (m) {
        case 2:
            if (f2() == -1)
                continue;
            break;
        case 3:
            if (f1() == -1)
                continue;
            break;
        }
        f3();
    }
}

/* B3 — badan TANPA `continue`, cuma `break`. */
pb3(n)
int n;
{
    int i;
    for (i = 0; i < n; i++) {
        switch (m) {
        case 3:
            f1();
            break;
        case 2:
            f2();
            break;
        }
        f3();
    }
}

/* B4 — TIGA case, urutan menurun 3,2,1. */
pb4(n)
int n;
{
    int i;
    for (i = 0; i < n; i++) {
        switch (m) {
        case 3:
            if (f1() == -1)
                continue;
            break;
        case 2:
            if (f2() == -1)
                continue;
            break;
        case 1:
            if (f3() == -1)
                continue;
            break;
        }
        f3();
    }
}

/* B5 — sama seperti B1 tapi dibungkus `if`, persis konteks main_. */
pb5(n, k)
int n, k;
{
    int i;
    for (i = 0; i < n; i++) {
        if (k == 1) {
            switch (m) {
            case 3:
                if (f1() == -1)
                    continue;
                break;
            case 2:
                if (f2() == -1)
                    continue;
                break;
            }
        }
        f3();
    }
}
