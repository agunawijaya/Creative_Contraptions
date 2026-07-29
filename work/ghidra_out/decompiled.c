// ==== entry @ 1000:000e ====

/* WARNING: Stack frame is not setup normally: Input value of stackpointer is not used */

void __cdecl16far entry(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  undefined1 *puVar4;
  undefined1 *puVar5;
  undefined2 unaff_ES;
  
  if ((*(int *)0x2 + 0xe6f9U & 0xf000) == 0) {
    iVar3 = (*(int *)0x2 + 0xe6f9U) * 0x10;
  }
  else {
    iVar3 = -0x10;
  }
  DAT_1907_0002 = 0x2560;
  DAT_1907_0000 = iVar3;
  *(undefined2 *)(iVar3 + -2) = unaff_ES;
  *(undefined2 *)(iVar3 + -4) = 0;
  puVar4 = (undefined1 *)0x81;
  uVar2 = (uint)*(byte *)0x80;
  iVar1 = -(uVar2 + 4 & 0xfffe);
  *(undefined1 *)(iVar3 + -4 + iVar1) = 99;
  puVar5 = (undefined1 *)(iVar3 + iVar1 + -3);
  if (uVar2 != 0) {
    *puVar5 = 0x20;
    puVar5 = (undefined1 *)(iVar3 + iVar1 + -2);
    do {
      *puVar5 = *puVar4;
      puVar4 = puVar4 + 1;
      puVar5 = puVar5 + 1;
      uVar2 = uVar2 - 1;
    } while (uVar2 != 0);
  }
  *puVar5 = 0;
  *(int *)(iVar3 + iVar1 + -6) = iVar3 + -4 + iVar1;
  *(undefined2 *)(iVar3 + iVar1 + -8) = 0x76;
  FUN_1000_70e8();
  return;
}



// ==== FUN_1000_0079 @ 1000:0079 ====

void __cdecl16far FUN_1000_0079(void)

{
  return;
}



// ==== FUN_1000_0082 @ 1000:0082 ====

/* WARNING: Removing unreachable block (ram,0x00010c16) */

void __cdecl16near FUN_1000_0082(void)

{
  int iVar1;
  undefined2 uVar2;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  int local_76 [50];
  int local_12;
  int local_10;
  int local_e;
  int local_c;
  uint local_8;
  int local_6;
  char local_4;
  
  FUN_1000_644a();
  FUN_1000_65e0();
  iVar1 = FUN_1000_5f90();
  if (iVar1 != 0) {
    FUN_1000_6a48();
    return;
  }
  uVar2 = *(undefined2 *)0x0;
  *(int *)0x84a = (int)&stack0xa10e;
  *(int *)0x73e = (int)&stack0x9894;
  local_12 = 0;
  *(int *)0x740 = (int)&stack0x91b0;
  *(int *)0x73a = (int)&stack0x9c18;
  *(int *)0x73c = (int)&stack0x92b8;
  *(undefined2 *)0x83a = uVar2;
  for (; local_12 < 0x14; local_12 = local_12 + 1) {
    *(undefined2 *)(local_12 * 2 + 0x76a) = 1;
  }
  for (local_12 = 0; local_12 < 0x14; local_12 = local_12 + 1) {
    *(undefined2 *)(local_12 * 2 + 0x742) = 1;
  }
  *(undefined2 *)0x266 = 0x140;
  *(undefined2 *)0x262 = 0x140;
  *(undefined2 *)0x2e2 = 0x284;
  *(undefined2 *)0x2e0 = 0x26c;
  iVar1 = FUN_1000_6b57();
  *(int *)0x846 = iVar1;
  if (iVar1 == -1) {
    FUN_1000_6a48();
    return;
  }
  FUN_1000_531d();
  FUN_1000_53ff();
  FUN_1000_53ff();
  FUN_1000_53ff();
  FUN_1000_53ff();
  FUN_1000_53ff();
  FUN_1000_53ff();
  iVar1 = FUN_1000_6b57();
  *(int *)0x72a = iVar1;
  if (iVar1 == -1) {
    FUN_1000_6a48();
    return;
  }
  iVar1 = FUN_1000_6b57();
  *(int *)0x72c = iVar1;
  if (iVar1 == -1) {
    FUN_1000_6a48();
    return;
  }
  iVar1 = FUN_1000_6b57();
  *(int *)0x72e = iVar1;
  if (iVar1 == -1) {
    FUN_1000_6a48();
    return;
  }
  FUN_1000_5db8();
  *(undefined2 *)0x792 = 0;
  *(undefined2 *)0x3b2 = 0x80;
  *(undefined2 *)0x734 = 1;
  *(undefined2 *)0x718 = 1;
  iVar1 = FUN_1000_5035();
  if (iVar1 < 0) {
    FUN_1000_6a48();
    return;
  }
  FUN_1000_171f();
  FUN_1000_531d();
  FUN_1000_531d();
  local_c = FUN_1000_531d();
  FUN_1000_531d();
  FUN_1000_131a();
  FUN_1000_149d();
  FUN_1000_498c();
  FUN_1000_3f0f();
  FUN_1000_18db();
  do {
    local_4 = FUN_1000_1814();
    if (local_4 == '\r') break;
  } while (local_4 != '\x1b');
  if (((local_4 != '\x1b') && (iVar1 = FUN_1000_312a(), iVar1 != -1)) &&
     (iVar1 = FUN_1000_31da(), iVar1 != -1)) {
    uVar2 = FUN_1000_5a78();
    local_12 = 0;
    *(undefined2 *)0x71a = uVar2;
    for (; local_12 < 0x14; local_12 = local_12 + 1) {
      FUN_1000_5a5b();
    }
switchD_1000_10e0_default:
    local_6 = 1;
    iVar1 = FUN_1000_341a();
    *(int *)0x792 = iVar1;
    if (iVar1 != -1) {
      if (*(int *)0x792 == 0) goto switchD_1000_0496_default;
      switch(*(int *)0x792) {
      case 1:
        *(undefined2 *)0x794 = 0;
        break;
      case 2:
      case 3:
      case 4:
        goto switchD_1000_0496_caseD_2;
      }
      goto switchD_1000_0496_default;
    }
  }
LAB_1000_10e8:
  FUN_1000_644a();
  *(undefined2 *)0x0 = *(undefined2 *)0x83a;
  return;
switchD_1000_0496_caseD_2:
  *(undefined2 *)0x794 = 1;
  iVar1 = FUN_1000_32bb();
  *(int *)0x734 = iVar1;
  if (iVar1 != -1) {
switchD_1000_0496_default:
    if (*(int *)0x792 != 0) {
      switch(*(int *)0x792) {
      case 1:
        *(undefined2 *)0x3b2 = 7;
        *(undefined2 *)0x736 = 1;
        *(undefined2 *)0x738 = 1;
        break;
      case 2:
        iVar1 = *(int *)0x734;
        *(undefined2 *)0x736 = 1;
        if (iVar1 == 1) {
          *(undefined2 *)0x738 = 1;
        }
        else {
          *(undefined2 *)0x738 = 2;
        }
        break;
      case 3:
        iVar1 = *(int *)0x734;
        *(undefined2 *)0x738 = 1;
        if (iVar1 == 1) {
          *(undefined2 *)0x736 = 1;
        }
        else {
          *(undefined2 *)0x736 = 2;
        }
        break;
      case 4:
        *(undefined2 *)0x738 = 3;
        *(undefined2 *)0x736 = 2;
      }
    }
switchD_1000_0509_default:
    *(undefined2 *)0x718 = 1;
    if ((*(int *)0x792 == 2) || (*(int *)0x792 == 3)) {
      iVar1 = FUN_1000_3322();
      *(int *)0x3b2 = iVar1;
      if (iVar1 == -1) goto switchD_1000_10e0_default;
      iVar1 = FUN_1000_5035();
      if (iVar1 < 0) goto LAB_1000_10e8;
      if (*(int *)0x792 == 3) {
        FUN_1000_1200();
      }
      if (local_6 == 1) {
        if (*(int *)0x792 == 2) {
          iVar1 = FUN_1000_30bb();
        }
        else {
          if (*(int *)0x792 != 3) goto LAB_1000_0582;
          iVar1 = FUN_1000_30e0();
        }
        if (iVar1 == -1) goto switchD_1000_10e0_default;
      }
LAB_1000_0582:
      local_6 = 0;
      FUN_1000_171f();
      FUN_1000_531d();
      local_8 = (uint)(*(int *)0x738 != 1);
      FUN_1000_531d();
    }
    *(undefined2 *)0x2e6 = 0;
    *(undefined2 *)0x51a = 0;
    *(undefined2 *)0x842 = 0;
    *(undefined2 *)0x71c = 0;
    local_c = FUN_1000_531d();
    FUN_1000_531d();
    if (*(int *)0x792 == 0) goto switchD_1000_10e0_default;
    switch(*(int *)0x792) {
    case 1:
      *(undefined2 *)0x51c = 0xffff;
      goto LAB_1000_0e0c;
    case 2:
      *(undefined2 *)0x842 = 1;
      *(undefined2 *)0x2e8 = 0;
      for (local_12 = 0; local_12 < *(int *)0x41c; local_12 = local_12 + 1) {
        iVar1 = local_12 * 2;
        *(undefined2 *)(&stack0x9110 + iVar1) = 0xffff;
        *(undefined2 *)(&stack0x9138 + iVar1) = 0xffff;
        *(undefined2 *)(&stack0x9188 + iVar1) = 0xffff;
        *(undefined2 *)(&stack0x9160 + iVar1) = 0xffff;
      }
      FUN_1000_131a();
      do {
        FUN_1000_498c();
        FUN_1000_3f0f();
        while (*(int *)0x842 != 0) {
          *(undefined2 *)0x842 = 0;
          FUN_1000_5936();
          uVar2 = FUN_1000_2e90();
          *(undefined2 *)0x2e8 = uVar2;
        }
        if (*(int *)0x2e8 != -1) {
          uVar2 = FUN_1000_18db();
          *(undefined2 *)0x842 = uVar2;
          iVar1 = FUN_1000_58c9();
          *(int *)0x2e8 = iVar1;
          if (iVar1 != 0) goto joined_r0x00010df1;
          if (*(int *)0x734 == 1) {
            FUN_1000_5954();
          }
          FUN_1000_171f();
        }
      } while (*(int *)0x2e8 != -1);
      goto switchD_1000_0509_default;
    case 3:
      *(undefined2 *)0x842 = 1;
      *(undefined2 *)0x2e8 = 0;
      for (local_12 = 0; local_12 < *(int *)0x4b4 + -1; local_12 = local_12 + 1) {
        iVar1 = local_12 * 2;
        *(undefined2 *)(&stack0x9070 + iVar1) = 0xffff;
        *(undefined2 *)(&stack0x9098 + iVar1) = 0xffff;
        *(undefined2 *)(&stack0x90e8 + iVar1) = 0xffff;
        *(undefined2 *)(&stack0x90c0 + iVar1) = 0xffff;
      }
      local_12 = *(int *)0x4b4 + -1;
      local_e = FUN_1000_4094();
      local_c = 0;
      while ((local_c < local_e &&
             ((uint)*(byte *)(*(int *)0x73c + local_76[local_c] * 0xc + 1) != *(uint *)0x3b2))) {
        local_c = local_c + 1;
      }
      iVar1 = local_12 * 2;
      *(int *)(&stack0x9070 + iVar1) = local_c;
      *(int *)(&stack0x9098 + iVar1) = local_76[local_c];
      *(undefined2 *)(&stack0x90e8 + iVar1) = *(undefined2 *)(local_12 * 6 + 0x4ba);
      *(undefined2 *)(&stack0x90c0 + iVar1) = 0xffff;
      FUN_1000_149d();
      do {
        FUN_1000_3f0f();
        FUN_1000_498c();
        while (*(int *)0x842 != 0) {
          *(undefined2 *)0x842 = 0;
          uVar2 = FUN_1000_2d11();
          *(undefined2 *)0x2e8 = uVar2;
        }
        if (*(int *)0x2e8 != -1) {
          uVar2 = FUN_1000_18db();
          *(undefined2 *)0x842 = uVar2;
          iVar1 = FUN_1000_58c9();
          *(int *)0x2e8 = iVar1;
          if (iVar1 != 0) goto joined_r0x00010df1;
          FUN_1000_171f();
        }
      } while (*(int *)0x2e8 != -1);
      goto switchD_1000_0509_default;
    case 4:
      iVar1 = FUN_1000_3105();
joined_r0x00010663:
      if (iVar1 != -1) {
        do {
          *(undefined2 *)0x732 = 0;
          *(undefined2 *)0x730 = 0;
          *(undefined2 *)0x7ec = 5;
          *(undefined2 *)0x7ee = 0x140;
          *(undefined2 *)0x82c = 4;
          *(undefined2 *)0x844 = 0;
          *(undefined2 *)0x3b2 = 0;
          *(undefined2 *)0x842 = 0;
          *(undefined2 *)0x2e8 = 0;
          *(undefined2 *)0x7e8 = 0;
          *(undefined2 *)0x848 = 0;
          *(undefined2 *)0x830 = 300;
          FUN_1000_4e01();
          *(undefined2 *)0x718 = 6;
          while( true ) {
            if (((*(int *)0x718 < 1) || (*(int *)0x2e8 == -1)) || (*(int *)0x848 != 0)) {
              iVar1 = *(int *)0x2e8;
              goto joined_r0x00010663;
            }
            if (*(int *)0x734 == 1) {
              *(undefined2 *)0x718 = 1;
            }
            if (*(int *)0x842 == 0) {
              *(undefined2 *)0x832 = 1;
              for (local_12 = 0; local_12 < 0x78; local_12 = local_12 + 1) {
                (&stack0x92b8)[local_12 * 0xc] = 0;
              }
              for (local_12 = 0; local_12 < 0x23; local_12 = local_12 + 1) {
                (&stack0x9c18)[local_12 * 0xc] = 0;
              }
              *(int *)0x3b2 = *(int *)0x3b2 + 1;
              iVar1 = FUN_1000_5035();
              if (iVar1 < 0) {
                FUN_1000_6a48();
                return;
              }
              FUN_1000_10fd();
              FUN_1000_171f();
              *(undefined2 *)0x71c = 0;
              *(undefined2 *)0x2e6 = 0;
              *(undefined2 *)0x51a = 0;
              local_c = FUN_1000_531d();
              local_8 = (uint)(*(int *)0x738 != 1);
              local_c = FUN_1000_531d();
              local_c = FUN_1000_531d();
              FUN_1000_531d();
              FUN_1000_131a();
              FUN_1000_149d();
            }
            else {
              FUN_1000_171f();
            }
            FUN_1000_498c();
            FUN_1000_3f0f();
            FUN_1000_5936();
            iVar1 = FUN_1000_5505();
            *(int *)0x2e8 = iVar1;
            if (iVar1 == 0xfe) break;
            if (*(int *)0x2e8 != -1) {
              uVar2 = FUN_1000_18db();
              *(undefined2 *)0x842 = uVar2;
              do {
                local_4 = FUN_1000_1814();
                if (local_4 == ' ') break;
              } while (local_4 != '\x1b');
              if (local_4 == '\x1b') {
                *(undefined2 *)0x2e8 = 0xffff;
              }
              else if (*(int *)0x734 == 1) {
                FUN_1000_5954();
              }
            }
            if (*(int *)0x734 == 1) {
              *(int *)0x718 = *(int *)0x718 + 1;
            }
            *(int *)0x718 = *(int *)0x718 + -1;
          }
        } while( true );
      }
      break;
    default:
      break;
    }
  }
  goto switchD_1000_10e0_default;
joined_r0x00010df1:
  if (iVar1 == -1) goto switchD_1000_10e0_default;
  goto switchD_1000_0509_default;
LAB_1000_0e0c:
  *(undefined2 *)0x792 = 2;
  *(undefined2 *)0x71c = 0;
  *(undefined2 *)0x718 = 0;
  FUN_1000_171f();
  *(undefined2 *)0x718 = 1;
  *(undefined2 *)0x792 = 1;
  FUN_1000_2fde();
  local_c = FUN_1000_531d();
  for (local_10 = 0; local_10 < 9; local_10 = local_10 + 1) {
    *(uint *)(local_10 * 6 + 0x422) = (uint)*(byte *)(local_10 + 0x870);
  }
  uVar2 = FUN_1000_3909();
  *(undefined2 *)0x3ac = uVar2;
  iVar1 = FUN_1000_3c4f();
  *(int *)0x2e8 = iVar1;
  if (iVar1 != -1) {
    iVar1 = FUN_1000_3020();
    *(int *)0x2e8 = iVar1;
    if (iVar1 == -1) goto switchD_1000_10e0_default;
    if (*(int *)0x2e8 != 0xd) {
      iVar1 = FUN_1000_5035();
      if (iVar1 < 0) {
        FUN_1000_6a48();
        return;
      }
      FUN_1000_171f();
      *(undefined2 *)0x71c = 0;
      FUN_1000_531d();
      FUN_1000_531d();
      local_c = FUN_1000_531d();
      FUN_1000_531d();
      FUN_1000_131a();
      FUN_1000_149d();
      do {
        FUN_1000_498c();
        FUN_1000_3f0f();
        FUN_1000_18db();
        do {
          do {
            iVar1 = FUN_1000_1791();
          } while (iVar1 == 0);
          local_4 = FUN_1000_1814();
          if (local_4 == '\x1b') goto switchD_1000_10e0_default;
          if (local_4 == '\r') goto LAB_1000_0e0c;
        } while (local_4 != ' ');
        *(undefined2 *)0x718 = 1;
        FUN_1000_171f();
      } while( true );
    }
    goto LAB_1000_0e0c;
  }
  goto switchD_1000_10e0_default;
}



// ==== FUN_1000_10fd @ 1000:10fd ====

int __cdecl16near FUN_1000_10fd(int param_1,int param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  int iVar2;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  int local_42;
  int local_40 [26];
  int local_c;
  int local_a;
  int local_8;
  int local_6;
  int local_4;
  
  if (param_3 == 1) {
    local_42 = FUN_1000_5a5b(1);
    local_42 = local_42 + 1;
  }
  else {
    local_42 = FUN_1000_5a5b(1);
    local_42 = local_42 + 3;
  }
  local_40[0] = 0;
  for (local_8 = 0; local_8 < param_1; local_8 = local_8 + 1) {
    local_40[local_8 + 1] = 0;
  }
  local_a = 0;
  while (((local_a <= local_42 && (local_40[0] < 0x19)) && (3 < param_1 + -3))) {
    iVar2 = FUN_1000_5a5b(param_1 + -3);
    local_c = iVar2 + 1;
    if (local_40[iVar2 + 2] == 0) {
      if ((local_40[iVar2 + 3] == 0) && (local_40[iVar2 + 1] == 0)) {
        local_a = local_a + 1;
        local_40[iVar2 + 2] = 1;
      }
      else {
        local_40[0] = local_40[0] + 1;
      }
    }
  }
  local_6 = 0;
  local_4 = 0;
  for (local_8 = 0; iVar1 = local_4, iVar2 = local_6, local_8 < param_1; local_8 = local_8 + 1) {
    if (*(int *)(param_2 + local_8 * 2) == -1) {
      local_6 = local_6 + 1;
      *(int *)(param_4 + iVar2 * 2) = local_40[local_8 + 1];
    }
    else {
      local_4 = local_4 + 1;
      *(int *)(param_5 + iVar1 * 2) = local_40[local_8 + 1];
    }
  }
  return local_a;
}



// ==== FUN_1000_1200 @ 1000:1200 ====

int __cdecl16near FUN_1000_1200(int param_1,int param_2,undefined2 param_3,int param_4,int param_5)

{
  undefined2 uVar1;
  int iVar2;
  int iVar3;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  int local_40 [26];
  int local_c;
  int local_a;
  int local_8;
  int local_6;
  int local_4;
  
  uVar1 = FUN_1000_5a5b(0xf);
  *(undefined2 *)0x836 = uVar1;
  uVar1 = FUN_1000_5a5b(0xf);
  *(undefined2 *)0x838 = uVar1;
  iVar2 = FUN_1000_5a5b(1);
  local_40[0] = 0;
  for (local_8 = 0; local_8 < param_1; local_8 = local_8 + 1) {
    local_40[local_8 + 1] = 0;
  }
  local_a = 0;
  while (((local_a <= iVar2 + 3 && (local_40[0] < 0x19)) && (3 < param_1 + -3))) {
    iVar3 = FUN_1000_5a5b(param_1 + -3);
    local_c = iVar3 + 1;
    if ((local_40[iVar3 + 2] == 0) && (*(int *)(param_2 + local_c * 2) == 1)) {
      if ((local_40[iVar3 + 3] == 0) && (local_40[local_c] == 0)) {
        local_a = local_a + 1;
        local_40[iVar3 + 2] = 1;
      }
      else {
        local_40[0] = local_40[0] + 1;
      }
    }
  }
  local_6 = 0;
  local_4 = 0;
  for (local_8 = 0; iVar3 = local_4, iVar2 = local_6, local_8 < param_1; local_8 = local_8 + 1) {
    if (*(int *)(param_2 + local_8 * 2) == -1) {
      local_6 = local_6 + 1;
      *(int *)(param_4 + iVar2 * 2) = local_40[local_8 + 1];
    }
    else {
      local_4 = local_4 + 1;
      *(int *)(param_5 + iVar3 * 2) = local_40[local_8 + 1];
    }
  }
  return local_a;
}



// ==== FUN_1000_131a @ 1000:131a ====

void __cdecl16near
FUN_1000_131a(undefined2 param_1,int param_2,undefined2 param_3,undefined2 param_4,
             undefined2 param_5,int param_6,int param_7,undefined2 param_8,int param_9,int param_10,
             int param_11,int param_12)

{
  int iVar1;
  byte *pbVar2;
  undefined2 unaff_DS;
  int local_a;
  int local_6;
  int local_4;
  
  local_a = 0;
  do {
    if (param_6 <= local_a) {
      FUN_1000_4e3e(param_1,param_2,param_3,param_4,param_5,param_6,param_7,param_8);
      return;
    }
    iVar1 = FUN_1000_4094(*(undefined2 *)(param_9 + local_a * 6 + 4),param_10);
    if ((*(int *)0x736 == 2) && (*(int *)(local_a * 2 + 0x742) != 0)) {
      local_4 = 0;
      do {
        local_6 = FUN_1000_5a5b(iVar1);
        local_4 = local_4 + 1;
        if (local_4 == 0x96) goto LAB_1000_13ac;
        pbVar2 = (byte *)(param_2 + *(int *)(param_10 + local_6 * 2) * 0xc);
      } while ((100 < pbVar2[1]) || (*pbVar2 < 0x80));
    }
    else {
LAB_1000_13ac:
      do {
        do {
          local_6 = FUN_1000_5a5b(iVar1);
          pbVar2 = (byte *)(param_2 + *(int *)(param_10 + local_6 * 2) * 0xc);
        } while (100 < pbVar2[1]);
      } while (0x7f < *pbVar2);
    }
    if ((0 < *(int *)0x3b2) && ((*(int *)0x3b2 < 7 && (local_a == param_6 + -1)))) {
      local_6 = 0;
      while ((local_6 < iVar1 &&
             ((uint)*(byte *)(param_2 + *(int *)(param_10 + local_6 * 2) * 0xc + 1) !=
              *(uint *)0x3b2))) {
        local_6 = local_6 + 1;
      }
    }
    *(int *)(param_11 + local_a * 2) = local_6;
    *(undefined2 *)(param_7 + local_a * 2) = *(undefined2 *)(param_10 + local_6 * 2);
    *(uint *)(param_12 + local_a * 2) =
         (uint)*(byte *)(param_2 + *(int *)(param_10 + local_6 * 2) * 0xc);
    local_a = local_a + 1;
  } while( true );
}



// ==== FUN_1000_149d @ 1000:149d ====

void __cdecl16near
FUN_1000_149d(undefined2 param_1,int param_2,undefined2 param_3,undefined2 param_4,
             undefined2 param_5,int param_6,int param_7,int param_8,int param_9,int param_10,
             int param_11,int param_12,undefined2 param_13,undefined2 param_14)

{
  undefined2 uVar1;
  int iVar2;
  undefined2 unaff_DS;
  undefined2 local_c;
  undefined2 local_a;
  
  *(undefined2 *)0x840 = 0;
  uVar1 = FUN_1000_3909(param_3,param_13,param_9,param_6,param_14);
  *(undefined2 *)0x840 = 1;
  local_c = 0;
  *(undefined2 *)0x3ac = uVar1;
  do {
    if (param_6 <= local_c) {
      FUN_1000_4e3e(param_1,param_2,param_3,param_4,param_5,param_6,param_7,param_8);
      return;
    }
    if ((*(int *)0x738 == 3) && (*(int *)(local_c * 2 + 0x76a) != 0)) {
      iVar2 = FUN_1000_5a5b(*(undefined2 *)0x3ac);
      *(uint *)(param_12 + local_c * 2) = (uint)*(byte *)(param_2 + iVar2 * 0xc);
    }
    else {
      *(undefined2 *)(param_12 + local_c * 2) = *(undefined2 *)(param_9 + local_c * 6 + 4);
    }
    for (local_a = 0; local_a < *(int *)0x3ac; local_a = local_a + 1) {
      if ((uint)*(byte *)(param_2 + (uint)*(byte *)(local_a + param_10) * 0xc) ==
          *(uint *)(param_12 + local_c * 2)) {
        *(int *)(param_11 + local_c * 2) = local_a;
        *(uint *)(param_7 + local_c * 2) = (uint)*(byte *)(param_10 + local_a);
        *(undefined2 *)(param_8 + local_c * 2) = 0xffff;
        break;
      }
    }
    local_c = local_c + 1;
  } while( true );
}



// ==== FUN_1000_15d0 @ 1000:15d0 ====

void __cdecl16near FUN_1000_15d0(int param_1,int param_2)

{
  undefined2 unaff_DS;
  int local_6;
  int local_4;
  
  for (local_6 = 0; local_6 < param_1; local_6 = local_6 + 1) {
    local_4 = local_6 + 0x41;
    FUN_1000_6453(&local_4,*(undefined2 *)(param_2 + local_6 * 4 + 2),
                  *(undefined2 *)(param_2 + local_6 * 4),1,1,3);
  }
  return;
}



// ==== FUN_1000_1620 @ 1000:1620 ====

void __cdecl16near FUN_1000_1620(int param_1)

{
  undefined2 unaff_DS;
  undefined2 local_6;
  undefined2 local_4;
  
  FUN_1000_6869(0,0,0x13f,7,3);
  FUN_1000_6869(0,8,0x13f,0x9f,1);
  if ((*(int *)0x792 == 0) || (*(int *)0x792 == 1)) {
    local_4 = 1;
  }
  else {
    local_4 = 0;
  }
  if ((*(int *)0x792 == 4) && (*(int *)0x732 != 0 || *(int *)0x730 != 0)) {
    FUN_1000_6869(0,0xa8,0x13f,199,0);
  }
  else {
    FUN_1000_6869(0,0xa0,0x13f,199,local_4);
  }
  FUN_1000_672f(0x526,0,0x88,8,0x30);
  for (local_6 = 0; local_6 < *(int *)0x718; local_6 = local_6 + 1) {
    *(undefined2 *)0x266 = 0x140;
    *(undefined2 *)0x262 = 0x140;
    FUN_1000_2a53(0,local_6 * 10);
  }
  if (((param_1 == 1) && (*(int *)0x792 != 0)) && (*(int *)0x792 != 1)) {
    FUN_1000_6869(0x10,0xc0,0x12f,199,1);
  }
  return;
}



// ==== FUN_1000_171f @ 1000:171f ====

void __cdecl16near
FUN_1000_171f(int param_1,int param_2,int param_3,undefined2 param_4,undefined2 param_5)

{
  undefined2 unaff_DS;
  
  if ((param_1 == 2) || (param_1 == 1)) {
    FUN_1000_1620(1);
  }
  else {
    FUN_1000_1620(0);
  }
  FUN_1000_15d0(param_4,param_5);
  if (*(int *)0x792 == 4) {
    FUN_1000_2a86(*(undefined2 *)0x730,*(undefined2 *)0x732,0);
  }
  else {
    FUN_1000_6453(*(undefined2 *)(param_2 + param_3 * 2),200,0,1,1,2);
  }
  return;
}



// ==== FUN_1000_1791 @ 1000:1791 ====

uint __cdecl16near FUN_1000_1791(void)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined2 unaff_DS;
  
  while( true ) {
    iVar1 = FUN_1000_7443();
    if (iVar1 == 0) {
      return 0;
    }
    uVar2 = FUN_1000_6853(0x100);
    if (uVar2 == 0) break;
    uVar3 = uVar2 & 0xff;
    if (uVar3 == 0) {
      if ((((uVar2 == 0x4b00) || (uVar2 == 0x4d00)) || (uVar2 == 0x4800)) || (uVar2 == 0x5000)) {
        return 1;
      }
      FUN_1000_6853(0);
    }
    else {
      if ((uVar3 != 0x53) && (uVar3 != 0x73)) {
        return uVar2 & 0xff;
      }
      FUN_1000_735a();
      *(uint *)0x83c = *(uint *)0x83c ^ 1;
    }
  }
  return 1;
}



// ==== FUN_1000_1814 @ 1000:1814 ====

char __cdecl16near FUN_1000_1814(void)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  undefined2 unaff_DS;
  char local_6;
  
  while( true ) {
    while( true ) {
      do {
        iVar2 = FUN_1000_7443();
      } while (iVar2 == 0);
      uVar3 = FUN_1000_6853(0x100);
      if (((((uVar3 == 0) || ((uVar3 & 0xff) != 0)) || (uVar3 == 0x4b00)) ||
          ((uVar3 == 0x4d00 || (uVar3 == 0x4800)))) || (uVar3 == 0x5000)) break;
      FUN_1000_6853(0);
    }
    cVar1 = FUN_1000_735a();
    if ((cVar1 != 'S') && (cVar1 != 's')) break;
    *(uint *)0x83c = *(uint *)0x83c ^ 1;
  }
  while ((local_6 = cVar1, local_6 != '\0' && (iVar2 = FUN_1000_6853(0x100), iVar2 != 0))) {
    cVar1 = FUN_1000_6853(0x100);
    if (cVar1 == '\0') {
      FUN_1000_6853(0);
      cVar1 = local_6;
    }
    else {
      cVar1 = FUN_1000_735a();
      if ((cVar1 == 'S') || (cVar1 == 's')) {
        *(uint *)0x83c = *(uint *)0x83c ^ 1;
        cVar1 = local_6;
      }
      else if (cVar1 != '\x1b') {
        cVar1 = local_6;
      }
    }
  }
  return local_6;
}



// ==== FUN_1000_18db @ 1000:18db ====

undefined2 __cdecl16near
FUN_1000_18db(int param_1,int param_2,int param_3,int param_4,int param_5,int param_6,int param_7,
             int param_8,int param_9)

{
  int *piVar1;
  uint *puVar2;
  uint uVar3;
  byte *pbVar4;
  int iVar5;
  undefined2 uVar6;
  undefined2 unaff_DS;
  int local_5e;
  int local_5c;
  int local_5a;
  undefined2 local_40;
  undefined2 local_3e;
  undefined2 local_3c;
  int local_2a;
  undefined2 local_22;
  int local_16;
  int local_e;
  
  local_16 = 0;
  local_2a = 0;
  if ((*(int *)0x792 != 0) && (*(int *)0x792 != 1)) {
    FUN_1000_6869(0,0xa8,0x13f,199,0);
  }
  FUN_1000_5a7f(0x670e);
  iVar5 = FUN_1000_1791();
  if (iVar5 == 0x1b) {
    *(undefined2 *)0x842 = 0xffff;
LAB_1000_2495:
    FUN_1000_5a74();
    *(undefined2 *)0x722 = 0;
    *(int *)0x720 = (int)&local_40;
    FUN_1000_5a76();
    FUN_1000_2692(1);
    FUN_1000_5ac9();
    return *(undefined2 *)0x842;
  }
  *(undefined2 *)0x844 = 0;
  *(undefined2 *)0x2e4 = 0x27;
  *(undefined2 *)0x262 = 0x140;
  *(undefined2 *)0x266 = 0x140;
  FUN_1000_5a74();
  *(undefined2 *)0x722 = 2;
  *(undefined2 *)0x720 = 0x978;
  FUN_1000_5a76();
  while( true ) {
    FUN_1000_2b11(0x10);
    FUN_1000_672f(0x586,0,0x88,8,0x30);
    FUN_1000_2b11(0x10);
    FUN_1000_672f(0x526,0,0x88,8,0x30);
    if (*(int *)0x2e4 == 0x7c0) {
      *(undefined2 *)0x2e4 = 0;
    }
    if (*(int *)0x2e4 < 1) break;
    FUN_1000_1791();
  }
  local_16 = *(int *)0x718 * 10;
  FUN_1000_5a74();
  local_40 = 500;
  local_3e = 0x5b4;
  local_3c = 0x10;
  *(undefined2 *)0x722 = 1;
  *(int *)0x720 = (int)&local_40;
  FUN_1000_5a76();
  for (local_5e = 0x78; local_16 <= local_5e; local_5e = local_5e + -2) {
    FUN_1000_2b11(2);
    if (local_5e != 0x78) {
      FUN_1000_6869(local_5e + 0x10,0,local_5e + 0x11,7,3);
    }
    FUN_1000_672f(0x5e6,0,local_5e,8,0x10);
    FUN_1000_1791();
  }
  for (local_5e = 0; local_5e < 2; local_5e = local_5e + 1) {
    FUN_1000_2b11(2);
    FUN_1000_6600(0,4,8,100,0xffff);
  }
  FUN_1000_6869(local_16 + -8,0,local_16 + 0x10,7,3);
  FUN_1000_5a74();
  *(undefined2 *)0x722 = 0;
  *(int *)0x720 = (int)&local_40;
  FUN_1000_5a76();
  FUN_1000_2692(9);
  *(undefined2 *)0x842 = 0;
  local_5a = 0;
  local_5c = 0;
  *(undefined2 *)0x266 = 0x140;
  *(undefined2 *)0x262 = 0x140;
  FUN_1000_36ef();
  local_5e = 0;
LAB_1000_1ab8:
  if ((param_6 + param_2 <= local_5e) || (*(int *)0x842 != 0)) goto LAB_1000_2450;
  FUN_1000_66fd(0x16,0);
  if (*(int *)(param_1 + local_5e * 2) == -1) {
    if (*(int *)(param_5 + local_5c * 2) != *(int *)(param_3 + local_5c * 6 + 4)) {
      *(undefined2 *)0x842 = 0xffff;
      *(int *)0x844 = local_5e;
      piVar1 = (int *)(local_5c * 2 + 0x7be);
      *piVar1 = *piVar1 + 1;
      *(int *)0x7e6 = *(int *)0x7e6 + 1;
      *(int *)0x7e8 = *(int *)0x7e8 + 1;
      *(int *)0x51a = local_5a;
      *(int *)0x2e6 = local_5c;
      FUN_1000_6a48(0x9dd,local_5e + 0x41U & 0xff);
LAB_1000_2450:
      if (local_2a == 0) {
        FUN_1000_2b77();
        if (((*(int *)0x734 == 2) && (*(int *)0x718 < 2)) ||
           ((*(int *)0x3b2 == 6 && (*(int *)0x842 == 0)))) {
          FUN_1000_24bb();
        }
        if (local_5e != param_6 + param_2) {
          FUN_1000_2504(0x9c5);
        }
        do {
          iVar5 = FUN_1000_1791();
        } while (iVar5 == 0);
      }
      goto LAB_1000_2495;
    }
    iVar5 = local_5c * 2;
    local_e = *(int *)(iVar5 + 0x7be);
    *(undefined2 *)(iVar5 + 0x7be) = 0x8ad0;
    *(undefined2 *)0x3ae = *(undefined2 *)(*(int *)(param_4 + iVar5) * 0xc + 0x1b0);
    local_22 = 0x1a8;
    iVar5 = local_5c;
  }
  else {
    if (*(int *)(param_9 + local_5a * 2) == *(int *)(param_7 + local_5a * 6 + 4)) {
      local_e = *(int *)(local_5a * 2 + 0x796);
      *(undefined2 *)(local_5a * 2 + 0x796) = 0x8ad0;
    }
    else {
      piVar1 = (int *)(local_5a * 2 + 0x796);
      *piVar1 = *piVar1 + 1;
      *(int *)0x7e6 = *(int *)0x7e6 + 1;
      *(int *)0x7e8 = *(int *)0x7e8 + 1;
      *(int *)0x844 = local_5e;
      *(undefined2 *)0x842 = 1;
      *(int *)0x2e6 = local_5c;
      *(int *)0x51a = local_5a;
      FUN_1000_6a48(0xa01,local_5e + 0x41U & 0xff);
    }
    local_22 = 4;
    *(undefined2 *)0x3ae = *(undefined2 *)(*(int *)(param_8 + local_5a * 2) * 0xc + 0xc);
    iVar5 = local_5a;
  }
  if (((local_5e != param_6 + param_2 + -1) && (*(int *)0x792 == 4)) && (*(int *)0x842 == 0)) {
    if (-1 < local_e) {
      if (*(int *)0x7e6 == 1) {
        puVar2 = (uint *)0x730;
        uVar3 = *puVar2;
        *puVar2 = *puVar2 + 500;
        *(int *)0x732 = *(int *)0x732 + (uint)(0xfe0b < uVar3);
      }
      else if (*(int *)0x7e6 == 0) {
        puVar2 = (uint *)0x730;
        uVar3 = *puVar2;
        *puVar2 = *puVar2 + 1000;
        *(int *)0x732 = *(int *)0x732 + (uint)(0xfc17 < uVar3);
      }
      else {
        puVar2 = (uint *)0x730;
        uVar3 = *puVar2;
        *puVar2 = *puVar2 + 0xfa;
        *(int *)0x732 = *(int *)0x732 + (uint)(0xff05 < uVar3);
      }
    }
    FUN_1000_2a86(*(undefined2 *)0x730,*(undefined2 *)0x732,1,iVar5 * 6);
  }
  while ((*(char *)*(undefined2 *)0x3ae != -1 && ((char *)*(undefined2 *)0x3ae != (char *)0x0))) {
    iVar5 = FUN_1000_1791();
    if (iVar5 == 0x1b) {
      *(undefined2 *)0x842 = 0xffff;
      goto LAB_1000_2495;
    }
    pbVar4 = (byte *)*(undefined2 *)0x3ae;
    *(int *)0x3ae = *(int *)0x3ae + 1;
    iVar5 = 0x44;
    do {
      if ((uint)*pbVar4 == *(uint *)(iVar5 + 0x23d4)) {
                    /* WARNING: Could not recover jumptable at 0x00012426. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        uVar6 = (*(code *)*(undefined2 *)(iVar5 + 0x23d6))();
        return uVar6;
      }
      iVar5 = iVar5 + -4;
    } while (-1 < iVar5);
  }
  if (*(int *)(param_1 + local_5e * 2) == -1) {
    local_5c = local_5c + 1;
  }
  else {
    local_5a = local_5a + 1;
  }
  local_5e = local_5e + 1;
  goto LAB_1000_1ab8;
}



// ==== FUN_1000_24bb @ 1000:24bb ====

void __cdecl16near FUN_1000_24bb(void)

{
  undefined2 unaff_DS;
  
  if (*(int *)0x792 == 4) {
    *(undefined2 *)0x848 = 1;
    FUN_1000_672f(0x646,0,0x6c,8,0x68);
    FUN_1000_6453(0xa26,0x7c,0,1,1,3);
  }
  return;
}



// ==== FUN_1000_2504 @ 1000:2504 ====

void __cdecl16near FUN_1000_2504(undefined2 param_1)

{
  undefined2 uVar1;
  undefined2 uVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined2 unaff_DS;
  int local_16;
  int local_12;
  int local_10;
  int local_c;
  int local_4;
  
  FUN_1000_2b34();
  if ((*(int *)0x262 != 0x140) && (*(int *)0x266 != 0x140)) {
    local_16 = 0;
    local_12 = 0;
    while ((local_16 < 6 && (iVar3 = FUN_1000_1791(), iVar3 == 0))) {
      switch(local_12) {
      case 0:
        local_10 = 8;
        iVar3 = FUN_1000_5a5b(0x10e);
        local_c = iVar3 + 0x14;
        break;
      case 1:
        local_c = 0x137;
        iVar3 = FUN_1000_5a5b(0x6f);
        local_10 = iVar3 + 0x1c;
        break;
      case 2:
        local_10 = 0x97;
        iVar3 = FUN_1000_5a5b(0x10e);
        local_c = iVar3 + 0x14;
        break;
      case 3:
        iVar3 = FUN_1000_5a5b(0x6f);
        local_10 = iVar3 + 0x1c;
        local_c = 0;
      }
      local_12 = local_12 + 1;
      if (3 < local_12) {
        local_12 = 0;
      }
      iVar3 = *(int *)0x25e - local_c;
      if (*(int *)0x25e < local_c) {
        iVar3 = -iVar3;
      }
      iVar4 = *(int *)0x260 - local_10;
      if (*(int *)0x260 < local_10) {
        iVar4 = -iVar4;
      }
      iVar5 = iVar3;
      if (iVar4 < iVar3) {
        iVar5 = iVar4;
        iVar4 = iVar3;
      }
      local_4 = (iVar4 + iVar5 / 2) / 4;
      if (0xb4 < local_4) {
        local_4 = 0x96;
      }
      *(undefined2 *)0x728 = 8;
      *(undefined2 *)0x722 = 1;
      uVar1 = *(undefined2 *)0x25e;
      uVar2 = *(undefined2 *)0x260;
      *(undefined2 *)0x724 = 500;
      *(undefined2 *)0x720 = 0x724;
      *(int *)0x726 = local_4 * 8 + 500;
      FUN_1000_29b0(0,uVar2,uVar1,local_10,local_c,local_4,0);
      local_16 = local_16 + 1;
    }
    FUN_1000_6524(param_1,*(undefined2 *)0x2e2);
    return;
  }
  FUN_1000_2b34();
  return;
}



// ==== FUN_1000_2692 @ 1000:2692 ====

void __cdecl16near FUN_1000_2692(int param_1)

{
  undefined2 unaff_DS;
  
  if (0 < param_1) {
    *(int *)0x2e4 = param_1;
  }
  do {
  } while (0 < *(int *)0x2e4);
  return;
}



// ==== FUN_1000_26ae @ 1000:26ae ====

void __cdecl16near FUN_1000_26ae(int param_1)

{
  undefined2 uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined2 unaff_DS;
  
  if (0 < param_1) {
    do {
    } while (0 < *(int *)0x2e4);
    *(int *)0x2e4 = param_1;
  }
  FUN_1000_5e3b();
  if (*(int *)0x2e0 == 0x26c) {
    *(undefined2 *)0x2e0 = 0x284;
    *(undefined2 *)0x2e2 = 0x26c;
  }
  else {
    *(undefined2 *)0x2e0 = 0x26c;
    *(undefined2 *)0x2e2 = 0x284;
  }
  uVar1 = *(undefined2 *)0x260;
  uVar2 = *(undefined2 *)0x268;
  uVar3 = *(undefined2 *)0x25e;
  *(undefined2 *)0x262 = *(undefined2 *)0x25c;
  *(undefined2 *)0x26a = uVar2;
  *(undefined2 *)0x264 = uVar3;
  *(undefined2 *)0x266 = uVar1;
  return;
}



// ==== FUN_1000_29b0 @ 1000:29b0 ====

void __cdecl16near
FUN_1000_29b0(undefined2 param_1,int param_2,int param_3,int param_4,int param_5,int param_6,
             undefined2 param_7)

{
  int iVar1;
  int iVar2;
  undefined2 unaff_DS;
  undefined2 local_6;
  
  for (local_6 = 1; local_6 < param_6; local_6 = local_6 + 1) {
    iVar1 = param_2 + ((param_4 - param_2) * local_6) / param_6;
    *(int *)0x25c = 199 - iVar1;
    iVar2 = param_3 + ((param_5 - param_3) * local_6) / param_6;
    *(int *)0x25e = iVar2;
    *(int *)0x260 = iVar1;
    *(int *)0x268 = iVar2 / 4;
    FUN_1000_26ae(param_7);
  }
  *(int *)0x260 = param_4;
  *(int *)0x25e = param_5;
  *(int *)0x25c = 199 - param_4;
  *(int *)0x268 = param_5 / 4;
  FUN_1000_26ae(param_7);
  *(undefined2 *)0x722 = 0;
  *(undefined2 *)0x720 = 0x724;
  return;
}



// ==== FUN_1000_2a53 @ 1000:2a53 ====

void __cdecl16near FUN_1000_2a53(int param_1,int param_2)

{
  undefined2 unaff_DS;
  
  *(int *)0x260 = param_1;
  *(int *)0x25e = param_2;
  *(int *)0x25c = 199 - param_1;
  *(int *)0x268 = param_2 / 4;
  FUN_1000_26ae(0);
  return;
}



// ==== FUN_1000_2a86 @ 1000:2a86 ====

void __cdecl16near FUN_1000_2a86(undefined2 param_1,undefined2 param_2,int param_3)

{
  undefined1 local_16 [20];
  
  FUN_1000_7464(local_16,0xa30,param_1,param_2);
  FUN_1000_6869(0xd0,0,0x110,7,3);
  FUN_1000_6453(local_16,0xd0,0,1,1,2);
  if (1 < param_3) {
    FUN_1000_5cbb(0,0,0x13f,7,1);
    FUN_1000_370e();
    FUN_1000_2b11(0x14);
    FUN_1000_5cbb(0,0,0x13f,7,1);
  }
  return;
}



// ==== FUN_1000_2b11 @ 1000:2b11 ====

void __cdecl16near FUN_1000_2b11(int param_1)

{
  undefined2 local_4;
  
  for (local_4 = 0; local_4 < param_1; local_4 = local_4 + 1) {
    FUN_1000_5da1();
    FUN_1000_5d98();
  }
  return;
}



// ==== FUN_1000_2b34 @ 1000:2b34 ====

void __cdecl16near FUN_1000_2b34(void)

{
  undefined2 uVar1;
  undefined2 unaff_DS;
  undefined2 local_4;
  
  for (local_4 = 0; local_4 < 0x20; local_4 = local_4 + 1) {
    uVar1 = FUN_1000_5a5b(2);
    FUN_1000_5d98();
    FUN_1000_65e0(uVar1,*(undefined2 *)0x524);
  }
  FUN_1000_65e0(*(undefined2 *)0x522,*(undefined2 *)0x524);
  return;
}



// ==== FUN_1000_2b77 @ 1000:2b77 ====

void __cdecl16near FUN_1000_2b77(void)

{
  bool bVar1;
  undefined2 unaff_DS;
  undefined2 local_6;
  
  if ((*(int *)0x792 != 0) && (*(int *)0x792 != 1)) {
    if (*(int *)0x792 == 4) {
      local_6 = 0x15;
    }
    else {
      local_6 = 0x14;
    }
    if (*(int *)0x842 == 0) {
      FUN_1000_6453(0xa37,0x80,local_6 * 8 + 2,1,1,3);
    }
  }
  if ((*(int *)0x3b2 == 6) && (*(int *)0x842 == 0)) {
    bVar1 = true;
  }
  else {
    bVar1 = false;
  }
  if ((*(int *)0x792 == 4) && ((bVar1 || ((*(int *)0x734 == 2 && (*(int *)0x718 < 2)))))) {
    *(undefined2 *)0x718 = 0;
    FUN_1000_6453(0xa3e,0x20,0xc0,1,1,2);
  }
  else if (*(int *)0x842 == 0) {
    if (*(int *)0x792 == 4) {
      FUN_1000_6453(0xa7b,0x38,0xc0,1,1,2);
    }
    else if (*(int *)0x792 == 0) {
      FUN_1000_6453(0xa95,0x48,0xc0,1,1,2);
    }
    else {
      if (*(int *)0x792 == 1) {
        FUN_1000_6453(0xaab,0x40,0xac,1,1,2);
        FUN_1000_6453(0xac1,0x40,0xb6,1,1,2);
      }
      else {
        FUN_1000_6453(0xad4,0x40,0xac,1,1,2);
        FUN_1000_6453(0xae9,0x40,0xb6,1,1,2);
      }
      FUN_1000_6453(0xafe,0x10,0xc0,1,1,2);
    }
  }
  else {
    FUN_1000_6453(0xa5d,0x28,0xc0,1,1,2);
  }
  return;
}



// ==== FUN_1000_2d11 @ 1000:2d11 ====

uint __cdecl16near
FUN_1000_2d11(int param_1,int param_2,int param_3,int param_4,int param_5,undefined2 param_6,
             undefined2 param_7,undefined2 param_8,undefined2 param_9)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  undefined2 local_6c [50];
  uint local_8;
  int local_6;
  uint local_4;
  
  local_6 = 0;
  while( true ) {
    FUN_1000_36ef();
    local_4 = 0;
    do {
      iVar1 = FUN_1000_4094(*(undefined2 *)(param_5 + *(int *)0x51a * 6 + 4),local_6c);
      if (0x32 < iVar1) {
        FUN_1000_6a48(0xb24,iVar1);
      }
      uVar2 = *(int *)0x51a * 6;
      local_4 = FUN_1000_42ca(*(undefined2 *)0x72c,param_7,*(undefined2 *)(uVar2 + param_5),
                              *(undefined2 *)(param_5 + uVar2 + 2),local_6c,iVar1,
                              *(undefined2 *)(param_2 + *(int *)0x51a * 2),
                              *(undefined2 *)(*(int *)0x51a * 2 + 0x742),uVar2);
      if (local_4 != 0xffff) {
        uVar2 = local_4 & 0x7fff;
        puVar3 = (uint *)(param_2 + *(int *)0x51a * 2);
        local_8 = uVar2;
        if (uVar2 != *puVar3) {
          local_6 = 1;
          *puVar3 = uVar2;
          *(undefined2 *)(param_3 + *(int *)0x51a * 2) = local_6c[local_4];
          *(uint *)(param_4 + *(int *)0x51a * 2) =
               (uint)*(byte *)(*(int *)0x73c + *(int *)(param_3 + *(int *)0x51a * 2) * 0xc);
        }
        iVar1 = *(int *)0x51a;
        *(int *)0x51a = iVar1 + 1;
        if (param_1 + -1 <= iVar1 + 1) {
          *(undefined2 *)0x51a = 0;
        }
      }
    } while (-1 < (int)local_4);
    if (local_4 == 0xffff) {
      return 0xffff;
    }
    iVar1 = FUN_1000_5911(uVar2);
    if (iVar1 == 0x1b) break;
    if (iVar1 != 0xd) {
LAB_1000_2e53:
      if ((local_6 == 1) && (local_4 != 0xffff)) {
        FUN_1000_4e3e(4,*(undefined2 *)0x73c,*(undefined2 *)0x72c,param_8,param_9,param_1,param_3,
                      param_6);
      }
      return local_4;
    }
  }
  local_4 = 0xffff;
  goto LAB_1000_2e53;
}



// ==== FUN_1000_2e90 @ 1000:2e90 ====

uint __cdecl16near
FUN_1000_2e90(undefined2 param_1,byte param_2,int param_3,undefined2 param_4,undefined2 param_5,
             int param_6,undefined2 param_7,int param_8,int param_9,undefined2 param_10,
             undefined2 param_11,undefined2 param_12)

{
  bool bVar1;
  undefined2 uVar2;
  uint *puVar3;
  uint uVar4;
  int iVar5;
  undefined2 unaff_DS;
  uint local_4;
  
  uVar2 = FUN_1000_3909(*(undefined2 *)0x72a,param_1,param_3,param_2,param_7);
  bVar1 = false;
  *(undefined2 *)0x3ac = uVar2;
  while( true ) {
    FUN_1000_36ef();
    FUN_1000_5936();
    do {
      puVar3 = (uint *)(*(int *)0x2e6 * 6);
      local_4 = FUN_1000_3c4f(param_1,*(undefined2 *)((int)puVar3 + param_3),
                              *(undefined2 *)((int)puVar3 + param_3 + 2),param_4,param_5,
                              *(undefined2 *)(param_6 + *(int *)0x2e6 * 2),puVar3);
      if (local_4 != 0xffff) {
        uVar4 = local_4 & 0x7fff;
        puVar3 = (uint *)(param_6 + *(int *)0x2e6 * 2);
        if (*puVar3 != uVar4) {
          bVar1 = true;
          *puVar3 = uVar4;
          *(uint *)(param_8 + *(int *)0x2e6 * 2) = (uint)*(byte *)(uVar4 + 0x2ea);
          *(uint *)(param_9 + *(int *)0x2e6 * 2) =
               (uint)*(byte *)(*(int *)0x73a + *(int *)(param_8 + *(int *)0x2e6 * 2) * 0xc);
        }
        iVar5 = *(int *)0x2e6;
        *(int *)0x2e6 = iVar5 + 1;
        if ((int)(uint)param_2 <= iVar5 + 1) {
          *(undefined2 *)0x2e6 = 0;
        }
      }
    } while (-1 < (int)local_4);
    if (local_4 == 0xffff) {
      return 0xffff;
    }
    iVar5 = FUN_1000_5911(puVar3);
    if (iVar5 == 0x1b) break;
    if (iVar5 != 0xd) {
LAB_1000_2f9e:
      if ((bVar1) && (local_4 != 0xffff)) {
        FUN_1000_4e3e(0x1a8,*(undefined2 *)0x73a,*(undefined2 *)0x72a,param_11,param_12,param_2,
                      param_8,param_10,0,0);
      }
      return local_4;
    }
  }
  local_4 = 0xffff;
  goto LAB_1000_2f9e;
}



// ==== FUN_1000_2fde @ 1000:2fde ====

void __cdecl16near FUN_1000_2fde(void)

{
  FUN_1000_6869(0,8,0x13f,0x9f,1);
  FUN_1000_381a(0xc04,7);
  FUN_1000_36ef();
  return;
}



// ==== FUN_1000_300b @ 1000:300b ====

void __cdecl16near FUN_1000_300b(void)

{
  FUN_1000_381a(0xca2,3);
  FUN_1000_36ef();
  return;
}



// ==== FUN_1000_3020 @ 1000:3020 ====

undefined2 __cdecl16near FUN_1000_3020(void)

{
  char cVar1;
  int iVar2;
  undefined2 unaff_DS;
  
  FUN_1000_3769(*(undefined2 *)(*(int *)0x51c * 2 + 0x14f6),
                *(undefined2 *)(*(int *)0x51c * 2 + 0x1508));
  FUN_1000_672f(*(int *)0x84a + (uint)*(byte *)(*(int *)0x51c + 0x7fa) * 0xc0,0x30,0x90,0x18,0x20);
  FUN_1000_381a(0x14d2,3);
  FUN_1000_36ef();
  do {
    do {
      iVar2 = FUN_1000_1791();
    } while (iVar2 == 0);
    cVar1 = FUN_1000_1814();
    if (cVar1 == '\x1b') {
      return 0xffff;
    }
    if (cVar1 == ' ') {
      FUN_1000_3734();
      return 0x20;
    }
  } while (cVar1 != '\r');
  FUN_1000_3734();
  return 0xd;
}



// ==== FUN_1000_30bb @ 1000:30bb ====

void __cdecl16near FUN_1000_30bb(void)

{
  FUN_1000_3769(0x1634,9);
  FUN_1000_34cc(0x1634,9);
  return;
}



// ==== FUN_1000_30e0 @ 1000:30e0 ====

void __cdecl16near FUN_1000_30e0(void)

{
  FUN_1000_3769(0x1796,0xb);
  FUN_1000_34cc(0x1796,0xb);
  return;
}



// ==== FUN_1000_3105 @ 1000:3105 ====

void __cdecl16near FUN_1000_3105(void)

{
  FUN_1000_3769(0x18f8,0xc);
  FUN_1000_34cc(0x18f8,0xc);
  return;
}



// ==== FUN_1000_312a @ 1000:312a ====

undefined2 __cdecl16near FUN_1000_312a(void)

{
  char cVar1;
  int iVar2;
  
  FUN_1000_3769(0x1a2a,2);
  FUN_1000_31b0(100);
  FUN_1000_381a(0x1a42,2);
  FUN_1000_31b0(100);
  FUN_1000_381a(0x1a5a,2);
  FUN_1000_31b0(100);
  FUN_1000_381a(0x1a72,1);
  FUN_1000_36ef();
  while( true ) {
    do {
      iVar2 = FUN_1000_1791();
    } while (iVar2 == 0);
    cVar1 = FUN_1000_1814();
    if (cVar1 == '\r') break;
    if (cVar1 == '\x1b') {
      return 0xffff;
    }
  }
  return 1;
}



// ==== FUN_1000_31b0 @ 1000:31b0 ====

void __cdecl16near FUN_1000_31b0(int param_1)

{
  int iVar1;
  int local_4;
  
  local_4 = 0;
  while( true ) {
    if (param_1 <= local_4) {
      return;
    }
    iVar1 = FUN_1000_1791();
    if (iVar1 != 0) break;
    FUN_1000_5da1();
    FUN_1000_5d98();
    local_4 = local_4 + 1;
  }
  return;
}



// ==== FUN_1000_31da @ 1000:31da ====

void FUN_1000_31da(void)

{
  int iVar1;
  int iVar2;
  
  FUN_1000_3769(0x1ad2,3);
  FUN_1000_36ef();
  do {
    do {
      iVar1 = FUN_1000_1791();
    } while (iVar1 == 0);
    iVar1 = FUN_1000_1814();
    iVar2 = 0x10;
    do {
      if (iVar1 == *(int *)(iVar2 + 0x3216)) {
                    /* WARNING: Could not recover jumptable at 0x00013234. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        (*(code *)*(undefined2 *)(iVar2 + 0x3218))();
        return;
      }
      iVar2 = iVar2 + -4;
    } while (-1 < iVar2);
  } while( true );
}



// ==== FUN_1000_32bb @ 1000:32bb ====

void __cdecl16near FUN_1000_32bb(void)

{
  int iVar1;
  int iVar2;
  undefined2 unaff_DS;
  
  iVar1 = *(int *)0x84a;
  iVar2 = FUN_1000_53ff(*(undefined2 *)0x846,*(undefined2 *)0x740,0xb,iVar1);
  FUN_1000_53ff(*(undefined2 *)0x846,*(undefined2 *)0x740,0xc,iVar1 + iVar2);
  *(int *)0x1b8a = iVar1;
  *(int *)0x1ba2 = iVar1 + iVar2;
  FUN_1000_3769(0x1b74,7);
  FUN_1000_34cc(0x1b74,7);
  return;
}



// ==== FUN_1000_3322 @ 1000:3322 ====

void __cdecl16near FUN_1000_3322(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  undefined2 unaff_DS;
  
  iVar1 = *(int *)0x84a;
  iVar2 = FUN_1000_53ff(*(undefined2 *)0x846,*(undefined2 *)0x740,0xd,iVar1);
  iVar2 = iVar1 + iVar2;
  iVar3 = FUN_1000_53ff(*(undefined2 *)0x846,*(undefined2 *)0x740,0xe,iVar2);
  iVar3 = iVar2 + iVar3;
  iVar4 = FUN_1000_53ff(*(undefined2 *)0x846,*(undefined2 *)0x740,0xf,iVar3);
  iVar4 = iVar3 + iVar4;
  iVar5 = FUN_1000_53ff(*(undefined2 *)0x846,*(undefined2 *)0x740,0x10,iVar4);
  iVar5 = iVar4 + iVar5;
  iVar6 = FUN_1000_53ff(*(undefined2 *)0x846,*(undefined2 *)0x740,0x11,iVar5);
  FUN_1000_53ff(*(undefined2 *)0x846,*(undefined2 *)0x740,0x12,iVar5 + iVar6);
  *(int *)0x1c86 = iVar4;
  *(int *)0x1c9e = iVar5;
  *(int *)0x1cb6 = iVar5 + iVar6;
  *(int *)0x1c56 = iVar2;
  *(int *)0x1c6e = iVar3;
  *(int *)0x1c3e = iVar1;
  FUN_1000_3769(0x1c28,0xf);
  FUN_1000_34cc(0x1c28,0xf);
  return;
}



// ==== FUN_1000_341a @ 1000:341a ====

void __cdecl16near FUN_1000_341a(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined2 unaff_DS;
  
  iVar1 = *(int *)0x84a;
  iVar2 = FUN_1000_53ff(*(undefined2 *)0x846,*(undefined2 *)0x740,7,iVar1);
  iVar2 = iVar1 + iVar2;
  iVar3 = FUN_1000_53ff(*(undefined2 *)0x846,*(undefined2 *)0x740,8,iVar2);
  iVar3 = iVar2 + iVar3;
  iVar4 = FUN_1000_53ff(*(undefined2 *)0x846,*(undefined2 *)0x740,9,iVar3);
  FUN_1000_53ff(*(undefined2 *)0x846,*(undefined2 *)0x740,10,iVar3 + iVar4);
  *(int *)0x1da6 = iVar3 + iVar4;
  *(int *)0x1d76 = iVar2;
  *(int *)0x1d8e = iVar3;
  *(int *)0x1d5e = iVar1;
  FUN_1000_3769(0x1d48,0xb);
  FUN_1000_34cc(0x1d48,0xb);
  return;
}



// ==== FUN_1000_34cc @ 1000:34cc ====

void FUN_1000_34cc(char *param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  char *pcVar6;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  int local_48;
  int local_46;
  int local_44;
  int local_42;
  char *local_40;
  int local_3e;
  int aiStack_34 [25];
  
  FUN_1000_36ef();
  local_46 = 0;
  local_40 = param_1;
  for (local_48 = 0; local_48 < param_2; local_48 = local_48 + 1) {
    if (*local_40 == -0x80) {
      aiStack_34[local_46] = local_48;
      local_46 = local_46 + 1;
    }
    local_40 = local_40 + 0xc;
  }
  if (((char *)*(int *)0x1dcc == param_1) && (0 < local_46)) {
    local_48 = *(int *)0x1dce;
  }
  else {
    local_48 = 0;
  }
  if (local_46 < local_48) {
    local_48 = 0;
  }
  do {
    pcVar6 = param_1 + aiStack_34[local_48] * 0xc;
    if ((*pcVar6 == -0x80) && (0 < local_46)) {
      iVar3 = *(int *)(pcVar6 + 2);
      iVar1 = *(int *)(pcVar6 + 4);
      uVar4 = (uint)(byte)pcVar6[6];
      uVar5 = (uint)(byte)pcVar6[7];
      do {
        for (local_44 = 0; local_44 < 2; local_44 = local_44 + 1) {
          FUN_1000_4009(iVar3,iVar1,uVar4,uVar5,1);
          FUN_1000_5cbb(iVar1 + 1,iVar3 + 1,iVar1 + 1,iVar3 + uVar4 + -2,1);
          iVar2 = iVar1 + uVar5 + -2;
          FUN_1000_5cbb(iVar2,iVar3 + 1,iVar2,iVar3 + uVar4 + -2,1);
          FUN_1000_5cbb(iVar1,iVar3 + -1,iVar1 + uVar5 + -1,iVar3 + -1,2);
          FUN_1000_5cbb(iVar1,iVar3 + uVar4,iVar1 + uVar5 + -1,iVar3 + uVar4,2);
          local_42 = 0;
          while ((local_42 < 0x14 && (iVar2 = FUN_1000_1791(), iVar2 == 0))) {
            FUN_1000_5da1();
            FUN_1000_5d98();
            local_42 = local_42 + 1;
          }
        }
        iVar2 = FUN_1000_1791();
      } while (iVar2 == 0);
    }
    else {
      do {
        iVar3 = FUN_1000_1791();
      } while (iVar3 == 0);
    }
    local_3e = FUN_1000_1814();
    if (local_3e == 0) {
      local_3e = FUN_1000_1814();
      local_3e = local_3e + 0x200;
    }
    iVar3 = 0x14;
    do {
      if (local_3e == *(int *)(iVar3 + 0x36c0)) {
                    /* WARNING: Could not recover jumptable at 0x000136e2. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        (*(code *)*(undefined2 *)(iVar3 + 0x36c2))();
        return;
      }
      iVar3 = iVar3 + -4;
    } while (-1 < iVar3);
  } while( true );
}



// ==== FUN_1000_36ef @ 1000:36ef ====

void __cdecl16near FUN_1000_36ef(void)

{
  int iVar1;
  
  while( true ) {
    iVar1 = FUN_1000_1791();
    if (iVar1 == 0) {
      return;
    }
    iVar1 = FUN_1000_1791();
    if (iVar1 == 0x1b) break;
    FUN_1000_1814();
  }
  return;
}



// ==== FUN_1000_370e @ 1000:370e ====

void __cdecl16near FUN_1000_370e(void)

{
  undefined2 unaff_DS;
  
  FUN_1000_5a74();
  *(undefined2 *)0x722 = 2;
  *(undefined2 *)0x720 = 0x1dd0;
  FUN_1000_5a76();
  FUN_1000_2692(5);
  return;
}



// ==== FUN_1000_3734 @ 1000:3734 ====

void __cdecl16near FUN_1000_3734(void)

{
  undefined2 unaff_DS;
  
  FUN_1000_5a7f(0x670e);
  FUN_1000_5a74();
  *(undefined2 *)0x722 = 2;
  *(undefined2 *)0x720 = 0x1ddb;
  FUN_1000_5a76();
  FUN_1000_2692(5);
  FUN_1000_5a74();
  FUN_1000_5ac9();
  return;
}



// ==== FUN_1000_3769 @ 1000:3769 ====

void __cdecl16near FUN_1000_3769(byte *param_1,int param_2)

{
  undefined2 unaff_DS;
  int local_4;
  
  FUN_1000_6869(0,0,0x13f,7,3);
  FUN_1000_672f(0x526,0,0x88,8,0x30);
  FUN_1000_6869(0,8,0x13f,199,1);
  for (local_4 = 0; local_4 < param_2; local_4 = local_4 + 1) {
    if (*param_1 < 0x80) {
      FUN_1000_6453(*(undefined2 *)(param_1 + 10),*(undefined2 *)(param_1 + 4),
                    *(undefined2 *)(param_1 + 2),param_1[7],param_1[6],param_1[8]);
    }
    else {
      FUN_1000_672f(*(undefined2 *)(param_1 + 10),*(undefined2 *)(param_1 + 2),
                    *(undefined2 *)(param_1 + 4),param_1[6],param_1[7]);
    }
    param_1 = param_1 + 0xc;
  }
  return;
}



// ==== FUN_1000_381a @ 1000:381a ====

void __cdecl16near FUN_1000_381a(byte *param_1,int param_2)

{
  undefined2 unaff_DS;
  int local_4;
  
  for (local_4 = 0; local_4 < param_2; local_4 = local_4 + 1) {
    if (*param_1 < 0x80) {
      FUN_1000_6453(*(undefined2 *)(param_1 + 10),*(undefined2 *)(param_1 + 4),
                    *(undefined2 *)(param_1 + 2),param_1[7],param_1[6],param_1[8]);
    }
    else {
      FUN_1000_672f(*(undefined2 *)(param_1 + 10),*(undefined2 *)(param_1 + 2),
                    *(undefined2 *)(param_1 + 4),param_1[6],param_1[7]);
    }
    param_1 = param_1 + 0xc;
  }
  return;
}



// ==== FUN_1000_3886 @ 1000:3886 ====

void __cdecl16near FUN_1000_3886(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = param_1 + 0x17;
  iVar3 = param_2 + 1;
  iVar2 = param_2 + 0x1e;
  FUN_1000_5cbb(iVar3,param_1,param_2 + 0x1d,param_1,3);
  FUN_1000_5cbb(iVar2,param_1,iVar2,param_1 + 0x16,3);
  FUN_1000_5cbb(param_2 + 2,iVar1,iVar2,iVar1,3);
  FUN_1000_5cbb(iVar3,param_1 + 1,iVar3,iVar1,3);
  return;
}



// ==== FUN_1000_3909 @ 1000:3909 ====

int __cdecl16near FUN_1000_3909(undefined2 param_1,int param_2,int param_3,int param_4)

{
  undefined1 uVar1;
  int iVar2;
  bool bVar3;
  char cVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  char *pcVar8;
  undefined2 unaff_DS;
  int local_1c;
  int local_1a;
  int local_18;
  int local_14;
  uint local_c;
  
  if (*(int *)0x71c == 0) {
    local_18 = 0;
  }
  else {
    local_18 = *(int *)0x3ac;
  }
  local_14 = 0;
  local_c = 0;
  while ((uVar6 = local_c, local_14 < param_4 &&
         (uVar6 = *(uint *)(param_3 + local_14 * 6 + 4), (int)uVar6 < 0x8c))) {
    local_14 = local_14 + 1;
  }
  local_c = uVar6;
  cVar4 = '\0';
  for (local_1c = 0; local_1c < 0x23; local_1c = local_1c + 1) {
    pcVar8 = (char *)(*(int *)0x73a + local_1c * 0xc);
    if (((local_1c == 0) || (*pcVar8 != pcVar8[-0xc])) || (pcVar8[1] != pcVar8[-0xb])) {
      bVar3 = true;
    }
    else {
      bVar3 = false;
    }
    if (bVar3) {
      for (local_14 = 0; local_14 < param_4; local_14 = local_14 + 1) {
        if ((*(int *)0x738 != 1) ||
           ((uint)*(byte *)(*(int *)0x73a + local_1c * 0xc) == *(uint *)(param_3 + local_14 * 6 + 4)
           )) {
          if (*(int *)0x840 != 0) {
            FUN_1000_53ff(param_1,*(undefined2 *)0x73a,local_1c,param_2);
          }
          param_2 = param_2 + 0xc0;
          if (*(int *)0x71c == 0) {
            *(char *)(local_18 + 0x7fa) = cVar4;
            *(undefined1 *)(local_18 + 0x2ea) = (char)local_1c;
            local_18 = local_18 + 1;
            cVar4 = cVar4 + '\x01';
          }
          break;
        }
      }
    }
    if (*(char *)(*(int *)0x73a + local_1c * 0xc + 0xc) == '\0') break;
  }
  if ((*(int *)0x71c == 0) && (*(int *)0x794 == 1)) {
    for (local_1c = 0; local_1c < local_18; local_1c = local_1c + 1) {
      iVar5 = FUN_1000_5a5b(local_18);
      uVar1 = *(undefined1 *)(iVar5 + 0x2ea);
      *(undefined1 *)(iVar5 + 0x2ea) = *(undefined1 *)(local_1c + 0x2ea);
      *(undefined1 *)(local_1c + 0x2ea) = uVar1;
      uVar1 = *(undefined1 *)(iVar5 + 0x7fa);
      *(undefined1 *)(iVar5 + 0x7fa) = *(undefined1 *)(local_1c + 0x7fa);
      *(undefined1 *)(local_1c + 0x7fa) = uVar1;
    }
    for (local_1c = 0; local_1c < local_18; local_1c = local_1c + 1) {
      uVar6 = (uint)*(byte *)(*(int *)0x73a + (uint)*(byte *)(local_1c + 0x2ea) * 0xc);
      iVar5 = local_1c;
      while (iVar2 = iVar5, local_1a = iVar2 + 1, local_1a < local_18) {
        uVar7 = (uint)*(byte *)(*(int *)0x73a + (uint)*(byte *)(iVar2 + 0x2eb) * 0xc);
        if ((uVar7 == uVar6) ||
           ((iVar5 = local_1a, 0x8b < uVar6 && (iVar5 = local_1a, 0x8b < uVar7)))) {
          if ((local_c != 0) && (uVar7 == local_c)) {
            *(undefined1 *)(local_1c + 0x2ea) = *(undefined1 *)(iVar2 + 0x2eb);
            *(undefined1 *)(local_1c + 0x7fa) = *(undefined1 *)(iVar2 + 0x7fb);
          }
          *(undefined1 *)(iVar2 + 0x2eb) = *(undefined1 *)(local_18 + 0x2e9);
          *(undefined1 *)(iVar2 + 0x7fb) = *(undefined1 *)(local_18 + 0x7f9);
          local_18 = local_18 + -1;
          iVar5 = iVar2;
        }
      }
    }
  }
  *(int *)0x71c = *(int *)0x71c + 1;
  return local_18;
}



// ==== FUN_1000_3b83 @ 1000:3b83 ====

void __cdecl16near FUN_1000_3b83(int param_1,int param_2)

{
  int iVar1;
  int iVar2;
  undefined2 unaff_DS;
  undefined2 local_8;
  
  if (param_1 == -1) {
    iVar2 = *(int *)0x3ac;
    *(int *)0x51c = iVar2 / 2;
    iVar1 = *(int *)0x51c;
    *(int *)0x51e = iVar2 / 2 + -4;
    *(int *)0x520 = iVar1 + 4;
  }
  else {
    *(int *)0x51c = param_1;
    *(int *)0x51e = param_1 + -4;
    *(int *)0x520 = param_1 + 4;
  }
  for (local_8 = 0; local_8 < 9; local_8 = local_8 + 1) {
    iVar2 = *(int *)0x51e + local_8;
    if ((SCARRY2(*(int *)0x51e,local_8) == iVar2 < 0) && (iVar2 < *(int *)0x3ac)) {
      FUN_1000_672f(param_2 + (uint)*(byte *)(*(int *)0x51e + local_8 + 0x7fa) * 0xc0,0xa8,
                    local_8 * -0x20 + 0x110,0x18,0x20);
    }
    else {
      FUN_1000_6869(local_8 * -0x20 + 0x110,0xa8,local_8 * -0x20 + 0x12f,0xbf,0,iVar2);
    }
  }
  return;
}



// ==== FUN_1000_3c4f @ 1000:3c4f ====

undefined2 __cdecl16near
FUN_1000_3c4f(int param_1,int param_2,undefined2 param_3,undefined2 param_4,undefined2 param_5,
             undefined2 param_6)

{
  bool bVar1;
  int iVar2;
  undefined2 uVar3;
  undefined2 unaff_DS;
  int local_a;
  int local_6;
  
  FUN_1000_3b83(param_6,param_1);
  if (param_2 != 0) {
    FUN_1000_672f(param_1 + (uint)*(byte *)(*(int *)0x51c + 0x7fa) * 0xc0,param_2,param_3,0x18,0x20)
    ;
  }
  while( true ) {
    *(undefined2 *)0x7ea = *(undefined2 *)0x7ec;
    do {
      if (param_2 != 0) {
        FUN_1000_3886(param_2,param_3);
      }
      FUN_1000_4cd4();
      FUN_1000_672f(0x364,0xc0,0x90,8,0x20);
      local_6 = 0;
      while ((local_6 < 0xc && (iVar2 = FUN_1000_1791(), iVar2 == 0))) {
        FUN_1000_5da1();
        FUN_1000_5d98();
        local_6 = local_6 + 1;
      }
      if (param_2 != 0) {
        FUN_1000_3886(param_2,param_3);
      }
      FUN_1000_672f(0x31c,0xc0,0x90,8,0x20);
      local_6 = 0;
      while ((local_6 < 0xc && (iVar2 = FUN_1000_1791(), iVar2 == 0))) {
        iVar2 = *(int *)0x7ea;
        *(int *)0x7ec = iVar2;
        if (iVar2 < 1) {
          FUN_1000_4bb9();
        }
        FUN_1000_5da1();
        FUN_1000_5d98();
        local_6 = local_6 + 1;
      }
      bVar1 = true;
      if ((*(int *)0x792 == 4) && (*(int *)0x7ee < 1)) {
        bVar1 = false;
      }
      iVar2 = *(int *)0x7ea;
      *(int *)0x7ec = iVar2;
      if (iVar2 < 1) {
        FUN_1000_4bb9();
      }
      iVar2 = FUN_1000_1791();
    } while ((iVar2 == 0) && (bVar1));
    if ((*(int *)0x792 == 4) && (*(int *)0x7ee < 1)) break;
    local_a = FUN_1000_1814();
    if (local_a == 0) {
      local_a = FUN_1000_1814();
      local_a = local_a + 0x100;
    }
    iVar2 = 0x18;
    do {
      if (local_a == *(int *)(iVar2 + 0x3edc)) {
                    /* WARNING: Could not recover jumptable at 0x00013f02. Too many branches */
                    /* WARNING: Treating indirect jump as call */
        uVar3 = (*(code *)*(undefined2 *)(iVar2 + 0x3ede))();
        return uVar3;
      }
      iVar2 = iVar2 + -4;
    } while (-1 < iVar2);
  }
  return 0xfe;
}



// ==== FUN_1000_3f0f @ 1000:3f0f ====

void __cdecl16near FUN_1000_3f0f(int param_1,int param_2,int param_3,int param_4,int *param_5)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined2 uVar4;
  undefined2 unaff_DS;
  int local_c;
  int local_6;
  
  iVar1 = *param_5;
  if (iVar1 == -1) {
    uVar4 = FUN_1000_3909(*(undefined2 *)0x72a,param_1,param_3,param_2);
    *(undefined2 *)0x3ac = uVar4;
  }
  for (local_c = 0; local_c < param_2; local_c = local_c + 1) {
    iVar2 = *(int *)(local_c * 6 + param_3);
    iVar3 = *(int *)(param_3 + local_c * 6 + 2);
    if ((*(int *)(param_4 + local_c * 2) < 0) || (param_5[local_c] < 0)) {
      FUN_1000_6869(iVar3 + 1,iVar2,iVar3 + 0x1e,iVar2 + 0x17,3,local_c * 2);
    }
    else {
      if (iVar1 != -1) {
        local_6 = *(int *)(param_5[local_c] * 0xc + 0x1ae);
      }
      else {
        local_6 = param_1 + *(int *)(param_4 + local_c * 2) * 0xc0;
      }
      FUN_1000_672f(local_6,iVar2,iVar3,0x18,0x20);
    }
  }
  return;
}



// ==== FUN_1000_4009 @ 1000:4009 ====

void __cdecl16near FUN_1000_4009(int param_1,int param_2,int param_3,int param_4,undefined2 param_5)

{
  int iVar1;
  
  if (param_2 == 0xff) {
    param_2 = 0x140 - param_4;
  }
  FUN_1000_5cbb(param_2,param_1,param_2 + param_4 + -2,param_1,param_5);
  iVar1 = param_2 + param_4 + -1;
  FUN_1000_5cbb(iVar1,param_1,iVar1,param_1 + param_3 + -1,param_5);
  iVar1 = param_1 + param_3 + -1;
  FUN_1000_5cbb(param_2 + 1,iVar1,param_2 + param_4 + -2,iVar1,param_5);
  FUN_1000_5cbb(param_2,param_1 + 1,param_2,param_1 + param_3 + -1,param_5);
  return;
}



// ==== FUN_1000_4094 @ 1000:4094 ====

int __cdecl16near FUN_1000_4094(uint param_1,int param_2)

{
  byte bVar1;
  int iVar2;
  bool bVar3;
  int *piVar4;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  int local_32;
  int local_30;
  byte local_2a;
  byte *local_28;
  int local_24;
  int local_22 [5];
  int local_18 [11];
  
  bVar3 = true;
  local_2a = 0xff;
  local_28 = (byte *)*(undefined2 *)0x73c;
  local_32 = 0;
  local_22[0] = 0;
  local_22[1] = 0;
  local_30 = 0;
  while ((local_32 < 0x78 && (bVar3))) {
    bVar1 = *local_28;
    if ((bVar1 & 0x7f) == param_1) {
      if (local_28[1] != local_2a) {
        if ((bVar1 & 0x80) == 0) {
          local_22[0] = local_22[0] + 1;
        }
        else {
          local_22[1] = local_22[1] + 1;
        }
        *(int *)(param_2 + local_30 * 2) = local_32;
        if (0x31 < local_30 + 1) {
          bVar3 = false;
        }
        local_2a = local_28[1];
        local_30 = local_30 + 1;
      }
    }
    else if (((int)param_1 < (int)(bVar1 & 0x7f)) || ((bVar1 & 0x7f) == 0)) {
      bVar3 = false;
    }
    local_28 = local_28 + 0xc;
    local_32 = local_32 + 1;
  }
  if ((*(int *)0x734 == 1) && ((*(int *)0x792 == 3 && (0 < local_22[1])))) {
    local_30 = 0;
    local_24 = 0;
    for (local_32 = 0; local_32 < 2; local_32 = local_32 + 1) {
      local_22[3] = *(int *)(local_32 * 2 + 0x836);
      local_22[2] = local_22[local_32];
      if (local_22[3] < local_22[2]) {
        local_18[0] = local_24 + local_22[3];
      }
      else {
        local_18[0] = local_24 + local_22[3] % local_22[2];
      }
      iVar2 = *(int *)(local_18[0] * 2 + param_2);
      local_18[local_30 + 1] = iVar2;
      if ((local_18[0] < 1) ||
         (*(byte *)(*(int *)0x73c + iVar2 * 0xc + 1) - 100 !=
          (uint)*(byte *)(*(int *)0x73c + *(int *)(param_2 + local_18[0] * 2 + -2) * 0xc + 1))) {
        piVar4 = (int *)(param_2 + local_18[0] * 2 + 2);
        iVar2 = local_30 + 1;
        if (*(byte *)(*(int *)0x73c + *piVar4 * 0xc + 1) - 100 ==
            (uint)*(byte *)(*(int *)0x73c + *(int *)(param_2 + local_18[0] * 2) * 0xc + 1)) {
          local_18[local_30 + 2] = *piVar4;
          iVar2 = local_30 + 2;
        }
      }
      else {
        local_18[local_30 + 1] = *(int *)(param_2 + local_18[0] * 2 + -2);
        local_18[local_30 + 2] = *(int *)(param_2 + local_18[0] * 2);
        iVar2 = local_30 + 2;
      }
      local_30 = iVar2;
      local_24 = local_24 + local_22[2];
    }
    for (local_32 = 0; local_32 < local_30; local_32 = local_32 + 1) {
      *(int *)(param_2 + local_32 * 2) = local_18[local_32 + 1];
    }
  }
  return local_30;
}



// ==== FUN_1000_42ca @ 1000:42ca ====

/* WARNING: Removing unreachable block (ram,0x0001471b) */
/* WARNING: Removing unreachable block (ram,0x0001451a) */
/* WARNING: Removing unreachable block (ram,0x00014566) */
/* WARNING: Removing unreachable block (ram,0x00014585) */
/* WARNING: Removing unreachable block (ram,0x00014580) */
/* WARNING: Removing unreachable block (ram,0x00014588) */
/* WARNING: Removing unreachable block (ram,0x000145a2) */
/* WARNING: Removing unreachable block (ram,0x0001459c) */
/* WARNING: Removing unreachable block (ram,0x000145a5) */

undefined2 __cdecl16near
FUN_1000_42ca(undefined2 param_1,undefined2 param_2,int param_3,int param_4,int param_5,int param_6,
             int param_7,int param_8)

{
  int iVar1;
  bool bVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  undefined2 uVar8;
  uint uVar9;
  byte *pbVar10;
  int *piVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;
  int *piVar15;
  undefined2 unaff_DS;
  int local_3c;
  int local_38;
  int local_34;
  int local_28;
  int local_26;
  int local_24;
  int local_22;
  int local_20;
  int local_1e;
  int local_1c;
  int local_1a;
  int local_18;
  int local_16;
  int local_14;
  int local_12;
  int local_c;
  
  iVar7 = *(int *)0x73c;
  if (*(int *)0x734 == 2) {
    *(undefined2 *)0x7f0 = 9;
  }
  else {
    *(undefined2 *)0x7f0 = 0x12;
  }
  if (0 < param_6) {
    if (param_7 < 0) {
      if (param_8 == 0) {
        do {
          do {
            param_7 = FUN_1000_5a5b(param_6);
            pbVar10 = (byte *)(*(int *)0x73c + *(int *)(param_5 + param_7 * 2) * 0xc);
          } while (100 < pbVar10[1]);
        } while (0x7f < *pbVar10);
      }
      else {
        local_c = 0;
        do {
          do {
            param_7 = FUN_1000_5a5b(param_6);
            local_c = local_c + 1;
            pbVar10 = (byte *)(*(int *)0x73c + *(int *)(param_5 + param_7 * 2) * 0xc);
          } while (100 < pbVar10[1]);
        } while ((*pbVar10 < 0x80) && (local_c < 0x73));
      }
    }
    iVar3 = param_7 * 2;
    piVar15 = (int *)(iVar3 + param_5);
    iVar1 = *piVar15;
    if ((param_7 + 1 < param_6) &&
       (piVar11 = (int *)(param_5 + iVar3 + 2),
       *(byte *)(*(int *)0x73c + *piVar11 * 0xc + 1) - 100 ==
       (uint)*(byte *)(*(int *)0x73c + iVar1 * 0xc + 1))) {
      iVar12 = iVar7 + *piVar11 * 0xc;
      uVar4 = (uint)*(byte *)(iVar12 + 4);
      if (0x7f < uVar4) {
        uVar4 = uVar4 - 0x100;
      }
      uVar13 = (uint)*(byte *)(iVar12 + 5);
      if (0x7f < uVar13) {
        uVar13 = uVar13 - 0x100;
      }
      FUN_1000_53ff(param_1,*(undefined2 *)0x73c,*piVar11,param_2,iVar3,piVar15,piVar11);
      FUN_1000_672f(param_2,param_3 + uVar4,param_4 + uVar13,*(undefined1 *)(iVar12 + 2),
                    *(undefined1 *)(iVar12 + 3));
    }
    if ((iVar1 < 0) || (0x78 < iVar1)) {
      FUN_1000_6a48(0x1de8,iVar1);
    }
    else {
      iVar12 = iVar7 + iVar1 * 0xc;
      uVar4 = (uint)*(byte *)(iVar12 + 4);
      if (0x7f < uVar4) {
        uVar4 = uVar4 - 0x100;
      }
      uVar13 = (uint)*(byte *)(iVar12 + 5);
      if (0x7f < uVar13) {
        uVar13 = uVar13 - 0x100;
      }
      uVar5 = (uint)*(byte *)(iVar12 + 2);
      uVar9 = (uint)*(byte *)(iVar12 + 3);
      local_20 = param_3 + uVar4;
      local_18 = param_4 + uVar13;
      local_1c = local_20 + uVar5;
      local_14 = local_18 + uVar9;
      if (param_7 + 0x141 != param_7) {
        if (param_7 + 1 < param_6) {
          iVar3 = param_7 * 2;
          piVar15 = (int *)(param_5 + iVar3 + 2);
          if (*(byte *)(*(int *)0x73c + *piVar15 * 0xc + 1) - 100 ==
              (uint)*(byte *)(*(int *)0x73c + *(int *)(param_5 + iVar3) * 0xc + 1)) {
            iVar7 = iVar7 + *piVar15 * 0xc;
            uVar6 = (uint)*(byte *)(iVar7 + 4);
            if (0x7f < uVar6) {
              uVar6 = uVar6 - 0x100;
            }
            uVar14 = (uint)*(byte *)(iVar7 + 5);
            if (0x7f < uVar14) {
              uVar14 = uVar14 - 0x100;
            }
            FUN_1000_53ff(param_1,*(undefined2 *)0x73c,*piVar15,param_2,iVar3,piVar15);
            local_20 = param_3 + uVar6;
            local_18 = param_4 + uVar14;
            local_1c = local_20 + (uint)*(byte *)(iVar7 + 2);
            local_14 = local_18 + (uint)*(byte *)(iVar7 + 3);
            FUN_1000_672f(param_2,local_20,local_18,(uint)*(byte *)(iVar7 + 2),
                          (uint)*(byte *)(iVar7 + 3));
          }
        }
        FUN_1000_53ff(param_1,*(undefined2 *)0x73c,iVar1,param_2,iVar3,piVar15);
        local_1e = param_3 + uVar4;
        local_16 = param_4 + uVar13;
        local_1a = local_1e + uVar5;
        local_12 = local_16 + uVar9;
        FUN_1000_672f(param_2,local_1e,local_16,uVar5,uVar9);
      }
    }
    iVar7 = local_18 - local_16;
    if (local_18 < local_16) {
      iVar7 = -iVar7;
    }
    if (iVar7 < 0x32) {
      if (local_1e < local_20) {
        local_20 = local_1e;
      }
      if (local_16 < local_18) {
        local_18 = local_16;
      }
      if (local_1c <= local_1a) {
        local_1c = local_1a;
      }
      local_24 = local_1c - local_20;
      if (local_14 <= local_12) {
        local_14 = local_12;
      }
      local_22 = local_14 - local_18;
      local_28 = local_20;
      local_26 = local_18;
    }
    else {
      local_24 = local_1a - local_1e;
      local_22 = local_12 - local_16;
      local_28 = local_1e;
      local_26 = local_16;
    }
    while( true ) {
      *(undefined2 *)0x7ea = *(undefined2 *)0x7ec;
      do {
        for (local_3c = 0; local_3c < 2; local_3c = local_3c + 1) {
          FUN_1000_4009(local_28,local_26,local_24,local_22,3);
          FUN_1000_4cd4();
          local_38 = 0;
          while ((local_38 < 0xc && (iVar7 = FUN_1000_1791(), iVar7 == 0))) {
            iVar7 = *(int *)0x7ea;
            *(int *)0x7ec = iVar7;
            if (iVar7 < 1) {
              FUN_1000_4bb9();
            }
            FUN_1000_5da1();
            FUN_1000_5d98();
            local_38 = local_38 + 1;
          }
        }
        bVar2 = true;
        if ((*(int *)0x792 == 4) && (*(int *)0x7ee < 1)) {
          bVar2 = false;
        }
        iVar7 = *(int *)0x7ea;
        *(int *)0x7ec = iVar7;
        if (iVar7 < 1) {
          FUN_1000_4bb9();
        }
        iVar7 = FUN_1000_1791();
      } while ((iVar7 == 0) && (bVar2));
      if ((*(int *)0x792 == 4) && (*(int *)0x7ee < 1)) break;
      local_34 = FUN_1000_1814();
      if (local_34 == 0) {
        local_34 = FUN_1000_1814();
        local_34 = local_34 + 0x100;
      }
      iVar7 = 0x18;
      do {
        if (local_34 == *(int *)(iVar7 + 0x4959)) {
                    /* WARNING: Could not recover jumptable at 0x0001497f. Too many branches */
                    /* WARNING: Treating indirect jump as call */
          uVar8 = (*(code *)*(undefined2 *)(iVar7 + 0x495b))();
          return uVar8;
        }
        iVar7 = iVar7 + -4;
      } while (-1 < iVar7);
    }
    return 0xfe;
  }
  return 0;
}



// ==== FUN_1000_498c @ 1000:498c ====

void __cdecl16near FUN_1000_498c(undefined2 param_1,int param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  undefined2 unaff_DS;
  int local_6a;
  undefined1 local_68 [100];
  int local_4;
  
  for (local_6a = 0; local_6a < param_2; local_6a = local_6a + 1) {
    if (-1 < *(int *)(param_4 + local_6a * 2)) {
      local_4 = FUN_1000_4094(*(undefined2 *)(param_3 + local_6a * 6 + 4),local_68);
      if (local_4 < 1) {
        FUN_1000_6a48(0x1e08,local_6a);
      }
      else {
        iVar1 = local_6a * 6;
        FUN_1000_4a31(*(undefined2 *)0x72c,param_1,*(undefined2 *)(iVar1 + param_3),
                      *(undefined2 *)(param_3 + iVar1 + 2),local_68,local_4,
                      *(undefined2 *)(param_4 + local_6a * 2),
                      *(undefined2 *)(param_5 + local_6a * 2),iVar1);
      }
    }
  }
  return;
}



// ==== FUN_1000_4a31 @ 1000:4a31 ====

void __cdecl16near
FUN_1000_4a31(undefined2 param_1,undefined2 param_2,int param_3,int param_4,int param_5,int param_6,
             int param_7,int param_8)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  undefined2 unaff_DS;
  undefined2 local_4;
  
  iVar1 = *(int *)(param_7 * 2 + param_5);
  iVar4 = *(int *)0x73c + iVar1 * 0xc;
  iVar2 = *(int *)(param_5 + param_7 * 2 + 2);
  iVar6 = *(int *)0x73c + iVar2 * 0xc;
  if ((param_7 + 1 < param_6) && (*(byte *)(iVar6 + 1) - 100 == (uint)*(byte *)(iVar4 + 1))) {
    uVar3 = (uint)*(byte *)(iVar6 + 4);
    if (0x7f < uVar3) {
      uVar3 = uVar3 - 0x100;
    }
    uVar5 = (uint)*(byte *)(iVar6 + 5);
    if (0x7f < uVar5) {
      uVar5 = uVar5 - 0x100;
    }
    if (param_8 < 0) {
      FUN_1000_53ff(param_1,*(undefined2 *)0x73c,iVar2,param_2);
      local_4 = param_2;
    }
    else {
      local_4 = *(undefined2 *)(((param_8 + iVar2) - iVar1) * 0xc + 10);
    }
    FUN_1000_672f(local_4,param_3 + uVar3,param_4 + uVar5,*(undefined1 *)(iVar6 + 2),
                  *(undefined1 *)(iVar6 + 3));
  }
  uVar3 = (uint)*(byte *)(iVar4 + 4);
  if (0x7f < uVar3) {
    uVar3 = uVar3 - 0x100;
  }
  uVar5 = (uint)*(byte *)(iVar4 + 5);
  if (0x7f < uVar5) {
    uVar5 = uVar5 - 0x100;
  }
  if (param_8 < 0) {
    FUN_1000_53ff(param_1,*(undefined2 *)0x73c,iVar1,param_2);
    local_4 = param_2;
  }
  else {
    local_4 = *(undefined2 *)(param_8 * 0xc + 10);
  }
  FUN_1000_672f(local_4,param_3 + uVar3,param_4 + uVar5,*(undefined1 *)(iVar4 + 2),
                *(undefined1 *)(iVar4 + 3));
  return;
}



// ==== FUN_1000_4bb9 @ 1000:4bb9 ====

void __cdecl16near FUN_1000_4bb9(void)

{
  undefined2 uVar1;
  int iVar2;
  undefined2 unaff_DS;
  
  if (*(int *)0x792 != 4) {
    return;
  }
  uVar1 = *(undefined2 *)0x7f0;
  iVar2 = *(int *)0x7ee + -1;
  *(undefined2 *)0x7ec = uVar1;
  *(undefined2 *)0x7ea = uVar1;
  *(int *)0x7ee = iVar2;
  if ((iVar2 < 0x140) && (-1 < iVar2)) {
    FUN_1000_6869(iVar2,0xa2,0x13f,0xa5,0);
    FUN_1000_5c84();
  }
  return;
}



// ==== FUN_1000_4c04 @ 1000:4c04 ====

void __cdecl16near FUN_1000_4c04(void)

{
  undefined2 unaff_DS;
  int local_a;
  undefined2 local_8;
  undefined2 local_6;
  undefined2 local_4;
  
  if (*(int *)0x792 == 4) {
    if ((*(int *)0x7ee < 0x140) && ((*(int *)0x718 != 6 || (*(int *)0x3b2 != 1)))) {
      if (-1 < *(int *)0x7ee) {
        FUN_1000_6869(0,0xa2,*(undefined2 *)0x7ee,0xa5,2);
        FUN_1000_6869(*(undefined2 *)0x7ee,0xa2,0x13f,0xa5,0);
      }
    }
    else {
      FUN_1000_5a74();
      local_8 = 500;
      local_6 = 0x474;
      local_4 = 0x10;
      *(undefined2 *)0x722 = 1;
      *(int *)0x720 = (int)&local_8;
      FUN_1000_5a76();
      for (local_a = 0; local_a < 0x140; local_a = local_a + 8) {
        FUN_1000_6869(local_a,0xa2,local_a + 7,0xa5,2);
        FUN_1000_2692(1);
      }
      FUN_1000_5a74();
      *(undefined2 *)0x722 = 0;
      *(int *)0x720 = (int)&local_8;
      FUN_1000_5a76();
    }
    return;
  }
  return;
}



// ==== FUN_1000_4cd4 @ 1000:4cd4 ====

void __cdecl16near FUN_1000_4cd4(void)

{
  int iVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  undefined2 uVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined2 unaff_DS;
  int local_6;
  int local_4;
  
  if ((*(int *)0x792 == 4) && (*(int *)0x734 == 2)) {
    if ((*(int *)0x7f2 < 1) || (*(int *)0x7ee == *(int *)0x82e)) {
      iVar1 = *(int *)0x7f8;
      *(undefined2 *)0x7f2 = 0x3c;
      if (0 < *(int *)0x7f6) {
        *(int *)0x7f6 = *(int *)0x7f6 + -1;
      }
      iVar6 = FUN_1000_5a5b(3);
      iVar8 = *(int *)0x7f6;
      iVar7 = FUN_1000_5a5b(3);
      iVar7 = iVar8 + iVar6 + iVar7;
      iVar8 = iVar7 + -2;
      *(int *)0x7f8 = iVar8;
      if ((iVar7 + -1 < 1) || (*(int *)0x3b4 <= iVar8)) {
        *(undefined2 *)0x7f8 = *(undefined2 *)0x7f6;
      }
      uVar2 = *(undefined2 *)(*(int *)0x7f8 * 4 + 0x3b6);
      uVar3 = *(undefined2 *)(*(int *)0x7f8 * 4 + 0x3b8);
      uVar4 = *(undefined2 *)(iVar1 * 4 + 0x3b6);
      uVar5 = *(undefined2 *)(iVar1 * 4 + 0x3b8);
      FUN_1000_5d98();
      if (iVar1 <= *(int *)0x3b4) {
        local_6 = iVar1 + 0x41;
        FUN_1000_6453(&local_6,uVar5,uVar4,1,1,3);
      }
      local_4 = 2;
      if (*(int *)0x830 <= *(int *)0x7ee) {
        local_4 = 0;
      }
      if (*(int *)0x7ee == *(int *)0x82e) {
        local_4 = 0;
        FUN_1000_4e01();
      }
      local_6 = *(int *)0x7f8 + 0x41;
      FUN_1000_6453(&local_6,uVar3,uVar2,1,1,local_4);
      if (local_4 == 0) {
        *(undefined2 *)0x834 = 1;
      }
      else {
        *(undefined2 *)0x834 = 0;
      }
    }
    return;
  }
  return;
}



// ==== FUN_1000_4e01 @ 1000:4e01 ====

void __cdecl16near FUN_1000_4e01(void)

{
  int iVar1;
  undefined2 unaff_DS;
  undefined2 local_4;
  
  *(undefined2 *)0x82e = 0xfc18;
  *(int *)0x82c = *(int *)0x82c + -1;
  for (local_4 = 0; local_4 < *(int *)0x82c; local_4 = local_4 + 1) {
    iVar1 = FUN_1000_5a5b(*(undefined2 *)0x830);
    if (*(int *)0x82e < iVar1) {
      *(int *)0x82e = iVar1;
    }
  }
  return;
}



// ==== FUN_1000_4e3e @ 1000:4e3e ====

int __cdecl16near
FUN_1000_4e3e(int param_1,int param_2,undefined2 param_3,int param_4,int param_5,int param_6,
             int param_7,int param_8)

{
  bool bVar1;
  uint uVar2;
  int iVar3;
  undefined1 *puVar4;
  char *pcVar5;
  char *pcVar6;
  undefined2 unaff_DS;
  char *local_1e;
  int local_1c;
  int local_1a;
  int local_18;
  int local_16;
  int local_14;
  int local_12;
  int local_10;
  int local_6;
  
  local_10 = param_5;
  local_18 = 0;
  local_12 = param_4;
  for (local_1a = 0; local_1a < param_6; local_1a = local_1a + 1) {
    *(int *)(param_8 + local_1a * 2) = local_18;
    local_14 = *(int *)(param_7 + local_1a * 2);
    local_16 = local_18;
    if (local_14 < 0) break;
    do {
      pcVar5 = (char *)(param_1 + local_16 * 0xc);
      pcVar6 = (char *)(param_2 + local_14 * 0xc);
      *pcVar5 = *pcVar6;
      pcVar5[1] = pcVar6[1];
      pcVar5[2] = pcVar6[2];
      pcVar5[3] = pcVar6[3];
      pcVar5[4] = pcVar6[4];
      pcVar5[5] = pcVar6[5];
      *(int *)(pcVar5 + 6) = local_12;
      iVar3 = FUN_1000_53ff(param_3,param_2,local_14,local_12);
      local_12 = local_12 + iVar3;
      local_18 = local_18 + 1;
      local_14 = local_14 + 1;
      local_16 = local_16 + 1;
      pcVar5 = (char *)(param_2 + local_14 * 0xc);
      if (*pcVar6 != *pcVar5) break;
      uVar2 = (uint)(byte)pcVar5[1];
    } while ((uVar2 == (byte)pcVar6[1]) || ((byte)pcVar6[1] + 100 == uVar2));
  }
  puVar4 = (undefined1 *)(param_1 + local_16 * 0xc);
  *puVar4 = 0;
  puVar4[1] = 0;
  puVar4[2] = 0;
  puVar4[3] = 0;
  puVar4[4] = 0;
  puVar4[5] = 0;
  *(undefined2 *)(puVar4 + 6) = 0;
  *(undefined2 *)(puVar4 + 8) = 0;
  local_6 = 0;
  do {
    if ((param_6 <= local_6) || (iVar3 = *(int *)(param_8 + local_6 * 2), iVar3 < 0)) {
      return local_18 + -1;
    }
    pcVar5 = (char *)(param_1 + iVar3 * 0xc);
    local_1e = (char *)*(undefined2 *)0x73e;
    local_1c = 0;
    bVar1 = false;
    for (; *local_1e != '\0'; local_1e = local_1e + 0xc) {
      if ((*local_1e == *pcVar5) && (local_1e[1] == pcVar5[1])) {
        *(int *)(pcVar5 + 8) = local_10;
        iVar3 = FUN_1000_53ff(*(undefined2 *)0x72e,*(undefined2 *)0x73e,local_1c,local_10);
        if (iVar3 != *(int *)(local_1e + 6)) {
          FUN_1000_6a48(0x1e1e);
        }
        local_10 = local_10 + *(int *)(local_1e + 6);
        bVar1 = true;
        break;
      }
      local_1c = local_1c + 1;
    }
    if (!bVar1) {
      (pcVar5 + 8)[0] = '\0';
      (pcVar5 + 8)[1] = '\0';
    }
    local_6 = local_6 + 1;
  } while( true );
}



// ==== FUN_1000_5035 @ 1000:5035 ====

undefined2 __cdecl16near FUN_1000_5035(int param_1)

{
  int iVar1;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  int local_120 [108];
  int local_48;
  int local_42;
  int local_40;
  int local_3e;
  int local_3c;
  int local_3a;
  int local_38;
  int local_36;
  int local_34;
  int local_32;
  
  local_42 = FUN_1000_6b57(0x1e3d,0x8004);
  if (local_42 == -1) {
    FUN_1000_6a48(0x1e45);
    return 0xffff;
  }
  iVar1 = FUN_1000_6d31(local_42,local_120,0xd8);
  if (iVar1 == -1) {
    FUN_1000_6a48(0x1e45);
  }
  else {
    local_48 = 0;
    local_3a = 0;
    while (((local_48 < 0x24 && (local_120[local_48 * 3] <= *(int *)0x3b2)) &&
           (local_120[local_48 * 3] != 0))) {
      if ((local_120[local_48 * 3] == *(int *)0x3b2) && (local_3a = local_3a + 1, local_3a == 1)) {
        local_38 = local_48;
      }
      local_48 = local_48 + 1;
    }
    if (local_3a != 0) {
      if (local_3a < param_1) {
        FUN_1000_6a48(0x1e45);
        param_1 = -1;
      }
      if (param_1 == -1) {
        do {
          local_36 = FUN_1000_5a5b(local_3a);
          local_36 = local_36 + local_38;
          if ((*(int *)0x1e2e != *(int *)0x3b2) || (local_3a < 2)) break;
        } while (local_36 == *(int *)0x1e30);
        *(undefined2 *)0x1e2e = *(undefined2 *)0x3b2;
        *(int *)0x1e30 = local_36;
      }
      else {
        local_36 = param_1 + local_38;
      }
      local_3e = local_120[local_36 * 3 + 2];
      local_40 = local_120[local_36 * 3 + 1];
      iVar1 = FUN_1000_6e8b(local_42,local_40,local_3e,0);
      if (-1 < iVar1) {
        FUN_1000_6d31(local_42,&local_3c,2);
        if (local_3c == *(int *)0x3b2) {
          local_34 = FUN_1000_6d31(local_42,0x3b4,2);
          iVar1 = FUN_1000_6d31(local_42,0x3b6,*(int *)0x3b4 << 2);
          local_34 = local_34 + iVar1;
          iVar1 = FUN_1000_6d31(local_42,0x3ac,2);
          local_34 = local_34 + iVar1;
          iVar1 = *(int *)0x3ac;
          *(int *)0x41c = iVar1;
          iVar1 = FUN_1000_6d31(local_42,0x41e,iVar1 * 6);
          local_34 = local_34 + iVar1;
          iVar1 = FUN_1000_6d31(local_42,0x4b4,2);
          local_34 = local_34 + iVar1;
          iVar1 = FUN_1000_6d31(local_42,0x4b6,*(int *)0x4b4 * 6);
          local_34 = local_34 + iVar1;
          iVar1 = FUN_1000_6d31(local_42,0x4f2,(*(int *)0x4b4 + *(int *)0x3ac) * 2);
          local_34 = local_34 + iVar1;
          local_32 = *(int *)0x3b4 * 4 + *(int *)0x3ac * 6 + 6 + *(int *)0x4b4 * 6 +
                     (*(int *)0x4b4 + *(int *)0x3ac) * 2;
          if (local_34 == local_32) {
            *(undefined2 *)0x41a = *(undefined2 *)0x3ac;
            local_48 = 0;
            *(undefined2 *)0x7e6 = 0;
            for (; local_48 < *(int *)0x4b4; local_48 = local_48 + 1) {
              *(undefined2 *)(local_48 * 2 + 0x796) = 0;
            }
            for (local_48 = 0; local_48 < *(int *)0x3ac; local_48 = local_48 + 1) {
              *(undefined2 *)(local_48 * 2 + 0x7be) = 0;
              *(undefined2 *)(local_48 * 2 + 0x3f2) = *(undefined2 *)(local_48 * 6 + 0x422);
            }
            FUN_1000_6fb6(local_42);
            return 1;
          }
        }
        else {
          FUN_1000_6a48(0x1e45);
        }
      }
    }
  }
  FUN_1000_6fb6(local_42);
  return 0xffff;
}



// ==== FUN_1000_5318 @ 1000:5318 ====

void __cdecl16near FUN_1000_5318(void)

{
  return;
}



// ==== FUN_1000_531d @ 1000:531d ====

uint __cdecl16near
FUN_1000_531d(undefined2 param_1,byte *param_2,int param_3,int param_4,int param_5)

{
  uint uVar1;
  bool bVar2;
  int iVar3;
  uint uVar4;
  undefined2 unaff_DS;
  uint local_e;
  uint local_a;
  
  iVar3 = FUN_1000_6e8b(param_1,0,0,0);
  local_a = iVar3 + 1;
  if (local_a == 0) {
    FUN_1000_6a48(0x1e52);
    return 0xffff;
  }
  local_e = 0;
  do {
    if (0x77 < (int)local_e) {
      return local_a;
    }
    iVar3 = FUN_1000_6d31(param_1,param_2,0xc);
    if (iVar3 != 0xc) {
      FUN_1000_6a48(0x1e63);
      return 0xffff;
    }
    uVar4 = (uint)*param_2;
    if (uVar4 == 0) {
      return local_e;
    }
    if (param_3 == 0) {
      bVar2 = false;
      for (local_a = 0; (int)local_a < param_5; local_a = local_a + 1) {
        uVar1 = *(uint *)(param_4 + local_a * 6 + 4);
        if (((uVar4 & 0x7f) == uVar1) || (uVar4 == uVar1)) {
          bVar2 = true;
          local_a = uVar1;
          break;
        }
      }
    }
    else {
      bVar2 = true;
      local_a = uVar4;
    }
    if (bVar2) {
      param_2 = param_2 + 0xc;
      local_e = local_e + 1;
    }
  } while( true );
}



// ==== FUN_1000_53ff @ 1000:53ff ====

/* WARNING: Removing unreachable block (ram,0x0001548e) */

undefined2 __cdecl16near
FUN_1000_53ff(undefined2 param_1,int param_2,int param_3,undefined2 param_4)

{
  int iVar1;
  int iVar2;
  undefined2 uVar3;
  int iVar4;
  int iVar5;
  undefined2 unaff_DS;
  bool bVar6;
  char cVar7;
  char cVar8;
  undefined1 local_5de [1500];
  
  iVar1 = *(int *)(param_2 + param_3 * 0xc + 6);
  iVar4 = 0;
  if (iVar1 < 0) {
    iVar4 = -1;
  }
  cVar8 = '\0';
  cVar7 = '\0';
  bVar6 = true;
  FUN_1000_751c();
  if (!bVar6 && cVar8 == cVar7) {
    FUN_1000_6a48(0x1e74,param_1,param_3);
    return 0xffff;
  }
  param_2 = param_2 + param_3 * 0xc;
  FUN_1000_6e8b(param_1,*(undefined2 *)(param_2 + 8),*(undefined2 *)(param_2 + 10),0);
  iVar2 = FUN_1000_6d31(param_1,local_5de,iVar1,iVar4);
  iVar5 = 0;
  if (iVar2 < 0) {
    iVar5 = -1;
  }
  if (iVar5 == iVar4 && iVar2 == iVar1) {
    uVar3 = FUN_1000_666a(local_5de,param_4,iVar1,iVar4);
    return uVar3;
  }
  FUN_1000_6a48(0x1ead);
  return 0xffff;
}



// ==== FUN_1000_5505 @ 1000:5505 ====

uint __cdecl16near
FUN_1000_5505(undefined2 param_1,byte param_2,int param_3,undefined2 param_4,undefined2 param_5,
             int param_6,undefined2 param_7,int param_8,int param_9,undefined2 param_10,
             undefined2 param_11,undefined2 param_12,int param_13,int param_14,int param_15,
             int param_16,int param_17,undefined2 param_18,undefined2 param_19,undefined2 param_20,
             undefined2 param_21)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  undefined2 uVar4;
  int iVar5;
  uint *puVar6;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  uint local_76;
  undefined2 local_6c [50];
  uint local_8;
  int local_6;
  int local_4;
  
  local_76 = 0;
  FUN_1000_5a7f(0x670e);
  *(undefined2 *)0x7f2 = 0xffff;
  iVar5 = *(int *)0x832;
  *(undefined2 *)0x7f6 = *(undefined2 *)0x3b4;
  local_6 = 0;
  bVar1 = false;
  if (iVar5 == 1) {
    iVar2 = FUN_1000_5a5b(200);
    iVar5 = *(int *)0x7ee;
    *(undefined2 *)0x832 = 0;
    *(int *)0x830 = iVar5 - ((iVar2 * 0x17) / 199 + 2);
  }
  else {
    *(undefined2 *)0x830 = 0x140;
  }
  if (*(int *)0x830 < *(int *)0x82e) {
    *(int *)0x82e = *(int *)0x7ee - *(int *)0x830;
  }
  FUN_1000_4c04();
  while( true ) {
    FUN_1000_36ef();
    FUN_1000_5936();
    while ((-1 < (int)local_76 && (local_76 != 0xfe))) {
      if (*(int *)(*(int *)0x844 * 2 + 0x4f2) == -1) {
        uVar4 = FUN_1000_3909(*(undefined2 *)0x72a,param_1,param_3,param_2,param_7);
        *(undefined2 *)0x3ac = uVar4;
        iVar5 = *(int *)0x2e6 * 6;
        local_76 = FUN_1000_3c4f(param_1,*(undefined2 *)(iVar5 + param_3),
                                 *(undefined2 *)(param_3 + iVar5 + 2),local_6c,param_5,
                                 *(undefined2 *)(param_6 + *(int *)0x2e6 * 2),iVar5);
        if ((local_76 != 0xffff) && (local_76 != 0xfe)) {
          uVar3 = local_76 & 0x7fff;
          puVar6 = (uint *)(param_6 + *(int *)0x2e6 * 2);
          if (*puVar6 != uVar3) {
            bVar1 = true;
            *puVar6 = uVar3;
            *(uint *)(param_8 + *(int *)0x2e6 * 2) = (uint)*(byte *)(uVar3 + 0x2ea);
            *(uint *)(param_9 + *(int *)0x2e6 * 2) =
                 (uint)*(byte *)(*(int *)0x73a + *(int *)(param_8 + *(int *)0x2e6 * 2) * 0xc);
          }
          iVar5 = *(int *)0x2e6;
          *(int *)0x2e6 = iVar5 + 1;
          if ((int)(uint)param_2 <= iVar5 + 1) {
            *(undefined2 *)0x2e6 = 0;
          }
        }
      }
      else {
        FUN_1000_6869(0,0xa8,0x13f,0xbf,0);
        uVar4 = FUN_1000_4094(*(undefined2 *)(param_17 + *(int *)0x51a * 6 + 4),local_6c);
        iVar5 = *(int *)0x51a * 6;
        local_76 = FUN_1000_42ca(*(undefined2 *)0x72c,param_19,*(undefined2 *)(iVar5 + param_17),
                                 *(undefined2 *)(param_17 + iVar5 + 2),local_6c,uVar4,
                                 *(undefined2 *)(param_14 + *(int *)0x51a * 2),iVar5);
        if ((local_76 != 0xffff) && (local_76 != 0xfe)) {
          local_8 = local_76 & 0x7fff;
          puVar6 = (uint *)(param_14 + *(int *)0x51a * 2);
          if (local_8 != *puVar6) {
            local_6 = 1;
            *puVar6 = local_8;
            *(undefined2 *)(param_15 + *(int *)0x51a * 2) = local_6c[local_76];
            *(uint *)(param_16 + *(int *)0x51a * 2) =
                 (uint)*(byte *)(*(int *)0x73c + *(int *)(param_15 + *(int *)0x51a * 2) * 0xc);
          }
          iVar5 = *(int *)0x51a;
          *(int *)0x51a = iVar5 + 1;
          if (param_13 + -1 <= iVar5 + 1) {
            *(undefined2 *)0x51a = 0;
          }
        }
      }
      iVar5 = *(int *)0x844;
      *(int *)0x844 = iVar5 + 1;
      if ((int)(param_13 + (uint)param_2 + -1) <= iVar5 + 1) {
        *(undefined2 *)0x844 = 0;
      }
    }
    if (local_76 == 0xfe) {
      FUN_1000_24bb();
      FUN_1000_6869(0,0xa0,0x13f,199,0);
      FUN_1000_6453(0x1ebe,0x38,0xb8,1,1,2);
      while( true ) {
        do {
          iVar5 = FUN_1000_1791();
        } while (iVar5 == 0);
        local_4 = FUN_1000_1814();
        if (local_4 == 0x1b) break;
        if (local_4 == 0x20) {
          FUN_1000_5ac9();
          return 0xfe;
        }
      }
      FUN_1000_5ac9();
      return 0xffff;
    }
    if ((local_76 == 0xffff) || (local_76 == 0xfe)) goto LAB_1000_58bd;
    iVar5 = FUN_1000_5911();
    if (iVar5 == 0x1b) break;
    if (iVar5 != 0xd) goto LAB_1000_5854;
    local_76 = 1;
  }
  local_76 = 0xffff;
LAB_1000_5854:
  if (bVar1) {
    FUN_1000_4e3e(0x1a8,*(undefined2 *)0x73a,*(undefined2 *)0x72a,param_11,param_12,param_2,param_8,
                  param_10,0,0);
  }
  if (local_6 == 1) {
    FUN_1000_4e3e(4,*(undefined2 *)0x73c,*(undefined2 *)0x72c,param_20,param_21,param_13,param_15,
                  param_18);
    local_6 = 0;
  }
LAB_1000_58bd:
  FUN_1000_5ac9();
  return local_76;
}



// ==== FUN_1000_58c9 @ 1000:58c9 ====

/* WARNING: Removing unreachable block (ram,0x0001590c) */

undefined2 __cdecl16near FUN_1000_58c9(void)

{
  int iVar1;
  undefined2 unaff_DS;
  
  while( true ) {
    while (iVar1 = FUN_1000_1814(), iVar1 == 0xd) {
      if (*(int *)0x842 == 0) {
        return 0x20;
      }
    }
    if (iVar1 == 0x1b) break;
    if (iVar1 == 0x20) {
      return 0;
    }
  }
  return 0xffff;
}



// ==== FUN_1000_5911 @ 1000:5911 ====

undefined2 __cdecl16near FUN_1000_5911(void)

{
  FUN_1000_6869(0,0xa8,0x13f,199,0);
  return 0x20;
}



// ==== FUN_1000_5936 @ 1000:5936 ====

void __cdecl16near FUN_1000_5936(void)

{
  FUN_1000_6869(0x10,0xc0,0x12f,199,1);
  return;
}



// ==== FUN_1000_5954 @ 1000:5954 ====

void __cdecl16near
FUN_1000_5954(undefined2 param_1,int param_2,undefined2 param_3,undefined2 param_4,
             undefined2 param_5,int param_6,int param_7,int param_8,int param_9,int param_10,
             int param_11,int param_12)

{
  bool bVar1;
  bool bVar2;
  int iVar3;
  undefined2 unaff_DS;
  undefined2 local_e;
  undefined2 local_c;
  
  local_e = 0;
  bVar2 = false;
  do {
    if (param_6 <= local_e) {
      if (bVar2) {
        FUN_1000_4e3e(param_1,param_2,param_3,param_4,param_5,param_6,param_7,param_8);
      }
      return;
    }
    iVar3 = local_e * 2;
    if (1 < *(int *)(iVar3 + 0x7be)) {
      *(undefined2 *)(param_12 + iVar3) = *(undefined2 *)(param_9 + local_e * 6 + 4);
      bVar1 = false;
      for (local_c = 0; local_c < *(int *)0x3ac; local_c = local_c + 1) {
        if ((uint)*(byte *)(param_2 + (uint)*(byte *)(local_c + param_10) * 0xc) ==
            *(uint *)(param_12 + local_e * 2)) {
          *(int *)(param_11 + local_e * 2) = local_c;
          *(uint *)(param_7 + local_e * 2) = (uint)*(byte *)(param_10 + local_c);
          *(undefined2 *)(param_8 + local_e * 2) = 0xffff;
          bVar2 = true;
          bVar1 = true;
          break;
        }
      }
      if (!bVar1) {
        FUN_1000_6a48(0x1ede,*(undefined2 *)(param_12 + local_e * 2),iVar3);
      }
    }
    local_e = local_e + 1;
  } while( true );
}



// ==== FUN_1000_5a5b @ 1000:5a5b ====

undefined2 __cdecl16near FUN_1000_5a5b(uint param_1)

{
  undefined2 unaff_DS;
  
  *(int *)0x71a = *(int *)0x71a * 0x3e85 + 0x3619;
  return (int)((ulong)param_1 * (ulong)*(uint *)0x71a >> 0x10);
}



// ==== FUN_1000_5a74 @ 1000:5a74 ====

void __cdecl16near FUN_1000_5a74(void)

{
  return;
}



// ==== FUN_1000_5a76 @ 1000:5a76 ====

void __cdecl16near FUN_1000_5a76(void)

{
  return;
}



// ==== FUN_1000_5a78 @ 1000:5a78 ====

undefined2 __cdecl16near FUN_1000_5a78(void)

{
  code *pcVar1;
  undefined2 extraout_DX;
  
  pcVar1 = (code *)swi(0x1a);
  (*pcVar1)();
  return extraout_DX;
}



// ==== FUN_1000_5a7f @ 1000:5a7f ====

void __cdecl16near FUN_1000_5a7f(undefined2 param_1)

{
  code *pcVar1;
  undefined2 unaff_DS;
  
  *(undefined2 *)0x1f00 = uRam00000070;
  *(undefined2 *)0x1f02 = uRam00000072;
  uRam00000070 = param_1;
  uRam00000072 = 0x1000;
  FUN_1000_5b23();
  *(undefined2 *)0x1f06 = 0xffff;
  pcVar1 = (code *)swi(0x21);
  (*pcVar1)();
  return;
}



// ==== FUN_1000_5ac9 @ 1000:5ac9 ====

void __cdecl16near FUN_1000_5ac9(void)

{
  undefined2 unaff_DS;
  
  uRam00000070 = *(undefined2 *)0x1f00;
  uRam00000072 = *(undefined2 *)0x1f02;
  FUN_1000_5b23();
  *(undefined2 *)0x1f06 = 0;
  return;
}



// ==== FUN_1000_5b23 @ 1000:5b23 ====

void __cdecl16near FUN_1000_5b23(void)

{
  undefined1 in_AL;
  char in_AH;
  undefined1 in_BL;
  undefined1 in_BH;
  
  out(0x43,in_AL);
  out((uint)(byte)(in_AH + 0x40),in_BL);
  out((uint)(byte)(in_AH + 0x40),in_BH);
  return;
}



// ==== FUN_1000_5b33 @ 1000:5b33 ====

undefined2 __cdecl16near FUN_1000_5b33(void)

{
  undefined2 in_AX;
  undefined1 in_CL;
  undefined1 in_CH;
  
  out(0x42,in_CL);
  out(0x42,in_CH);
  return in_AX;
}



// ==== FUN_1000_5b3e @ 1000:5b3e ====

undefined2 __cdecl16near FUN_1000_5b3e(void)

{
  byte bVar1;
  undefined2 in_AX;
  undefined2 unaff_DS;
  
  if (*(int *)0x83c != 0) {
    bVar1 = in(0x61);
    out(0x61,bVar1 | 3);
  }
  return in_AX;
}



// ==== FUN_1000_5b4e @ 1000:5b4e ====

undefined2 __cdecl16near FUN_1000_5b4e(void)

{
  byte bVar1;
  undefined2 in_AX;
  
  bVar1 = in(0x61);
  out(0x61,bVar1 & 0xfc);
  return in_AX;
}



// ==== FUN_1000_5b57 @ 1000:5b57 ====

undefined4 __cdecl16near FUN_1000_5b57(void)

{
  undefined2 in_AX;
  int in_CX;
  undefined2 in_DX;
  
  if (in_CX == 0) {
    FUN_1000_5b4e();
  }
  else {
    FUN_1000_5b3e();
  }
  return CONCAT22(in_DX,in_AX);
}



// ==== FUN_1000_5c84 @ 1000:5c84 ====

void __cdecl16near FUN_1000_5c84(void)

{
  int iVar1;
  undefined2 unaff_DS;
  
  if (*(int *)0x1f04 == 0) {
    *(undefined2 *)0x1f04 = 1;
  }
  else {
    *(undefined2 *)0x1f04 = 0;
  }
  FUN_1000_5b57();
  FUN_1000_5b33();
  FUN_1000_5da1();
  FUN_1000_5b3e();
  iVar1 = 8;
  do {
    FUN_1000_5d98();
    FUN_1000_5da1();
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  FUN_1000_5b4e();
  return;
}



// ==== FUN_1000_5cbb @ 1000:5cbb ====

void __cdecl16near FUN_1000_5cbb(uint param_1,uint param_2,uint param_3,int param_4,uint param_5)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  byte bVar5;
  uint uVar6;
  byte bVar7;
  int iVar8;
  byte *pbVar9;
  byte *pbVar10;
  undefined2 unaff_DS;
  
  pbVar9 = (byte *)((param_2 & 0xfe) * 8 + (CONCAT11((char)param_2,(char)param_2) & 0x1fe) * 0x20 +
                   ((int)param_1 >> 2));
  iVar4 = (param_4 - param_2) + 1;
  iVar8 = ((int)param_3 >> 2) - ((int)param_1 >> 2);
  bVar1 = *(byte *)((param_5 & 3) + 0x1f30);
  uVar2 = *(uint *)(((param_1 & 3) * 4 + (param_3 & 3)) * 2 + 0x1f10);
  uVar6 = CONCAT11(bVar1,bVar1) & uVar2;
  do {
    bVar5 = (byte)(uVar2 >> 8);
    bVar7 = (byte)(uVar6 >> 8);
    pbVar10 = pbVar9;
    if (iVar8 != 0) {
      *pbVar9 = *pbVar9 ^ bVar7;
      iVar3 = iVar8;
      while( true ) {
        iVar3 = iVar3 + -1;
        pbVar10 = pbVar10 + 1;
        if (iVar3 == 0) break;
        *pbVar10 = *pbVar10 ^ bVar1;
      }
      bVar5 = 0xff;
    }
    bVar5 = (byte)uVar6 & bVar5 & (byte)uVar2;
    uVar6 = CONCAT11(bVar7,bVar5);
    *pbVar10 = *pbVar10 ^ bVar5;
    if (((uint)pbVar9 & 0x2000) != 0) {
      pbVar9 = pbVar9 + 0x50;
    }
    pbVar9 = (byte *)((uint)pbVar9 ^ 0x2000);
    iVar4 = iVar4 + -1;
  } while (iVar4 != 0);
  return;
}



// ==== FUN_1000_5d98 @ 1000:5d98 ====

void __cdecl16near FUN_1000_5d98(void)

{
  byte bVar1;
  
  do {
    bVar1 = in(0x3da);
  } while ((bVar1 & 8) == 0);
  return;
}



// ==== FUN_1000_5da1 @ 1000:5da1 ====

void __cdecl16near FUN_1000_5da1(void)

{
  byte bVar1;
  
  do {
    bVar1 = in(0x3da);
  } while ((bVar1 & 8) != 0);
  return;
}



// ==== FUN_1000_5db8 @ 1000:5db8 ====

void __cdecl16near FUN_1000_5db8(void)

{
  uRam0000007c = 8000;
  uRam0000007e = 0x1907;
  return;
}



// ==== FUN_1000_5dce @ 1000:5dce ====

void __cdecl16near FUN_1000_5dce(uint param_1,int param_2,int param_3,uint param_4,int param_5)

{
  undefined1 *puVar1;
  undefined1 *puVar2;
  undefined1 *puVar3;
  uint uVar4;
  undefined1 *puVar5;
  undefined1 *puVar6;
  undefined1 *puVar7;
  undefined2 unaff_DS;
  
  uVar4 = param_2 + param_4;
  if (uVar4 != 0) {
    uVar4 = uVar4 - 1;
  }
  puVar3 = (undefined1 *)((param_1 >> 1) * *(int *)0x1f60 + (uVar4 >> 2));
  if ((param_1 & 1) != 0) {
    puVar3 = (undefined1 *)((uint)puVar3 ^ 0x2000);
  }
  puVar5 = puVar3 + -param_5;
  uVar4 = param_4 >> 2;
  puVar7 = puVar3;
  puVar6 = puVar5;
  do {
    for (; uVar4 != 0; uVar4 = uVar4 - 1) {
      puVar2 = puVar3;
      puVar3 = puVar3 + -1;
      puVar1 = puVar5;
      puVar5 = puVar5 + -1;
      *puVar2 = *puVar1;
    }
    if (0x1fff < (int)puVar6) {
      puVar6 = puVar6 + 0x50;
      puVar7 = puVar7 + 0x50;
    }
    puVar3 = (undefined1 *)((uint)puVar7 ^ 0x2000);
    puVar5 = (undefined1 *)((uint)puVar6 ^ 0x2000);
    param_3 = param_3 + -1;
    uVar4 = param_4 >> 2;
    puVar7 = puVar3;
    puVar6 = puVar5;
  } while (param_3 != 0);
  return;
}



// ==== FUN_1000_5e3b @ 1000:5e3b ====

void __cdecl16near FUN_1000_5e3b(void)

{
  undefined2 uVar1;
  undefined2 uVar2;
  undefined2 uVar3;
  undefined2 uVar4;
  int iVar5;
  undefined2 unaff_DS;
  
  iVar5 = (*(int *)0x25e % 4) * 2;
  uVar1 = *(undefined2 *)(iVar5 + 0x2d4);
  uVar2 = *(undefined2 *)0x2e0;
  uVar3 = *(undefined2 *)0x25e;
  uVar4 = *(undefined2 *)0x260;
  *(undefined2 *)0x2dc = *(undefined2 *)(iVar5 + 0x2cc);
  *(undefined2 *)0x2de = uVar1;
  FUN_1000_6939(uVar4,uVar3,uVar2);
  FUN_1000_5ea6(*(undefined2 *)0x2e0,*(undefined2 *)0x2e2,0x29c,0x2b4);
  FUN_1000_6524(0x2b4,*(undefined2 *)0x2e2);
  FUN_1000_657c(*(undefined2 *)0x2e0,*(undefined2 *)0x2de,*(undefined2 *)0x2dc);
  return;
}



// ==== FUN_1000_5ea6 @ 1000:5ea6 ====

void __cdecl16near
FUN_1000_5ea6(undefined1 *param_1,int param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined2 unaff_DS;
  int local_16;
  int local_14;
  undefined1 *local_6;
  undefined1 *local_4;
  
  if (*(int *)0x260 != 0x140) {
    local_6 = param_3;
    local_4 = param_4;
    for (local_16 = 0; local_16 < 0x18; local_16 = local_16 + 1) {
      *local_4 = 0;
      *local_6 = 0;
      local_6 = local_6 + 1;
      local_4 = local_4 + 1;
    }
    iVar1 = *(int *)0x260;
    iVar2 = *(int *)0x266;
    iVar3 = *(int *)0x26a;
    iVar4 = *(int *)0x268;
    for (local_16 = *(int *)0x260; local_16 < iVar1 + 8; local_16 = local_16 + 1) {
      if ((local_16 < *(int *)0x266) || (iVar2 + 8 <= local_16)) {
        param_3 = param_3 + 3;
        param_1 = param_1 + 3;
      }
      else {
        iVar5 = *(int *)0x266;
        iVar6 = *(int *)0x26a;
        for (local_14 = *(int *)0x268; local_14 < iVar4 + 3; local_14 = local_14 + 1) {
          if ((*(int *)0x26a <= local_14) && (local_14 < iVar3 + 3)) {
            iVar7 = ((local_16 - iVar5) * 3 - iVar6) + local_14;
            *param_1 = *(undefined1 *)(param_2 + iVar7);
            *param_3 = 0xff;
            param_4[iVar7] = 0xff;
          }
          param_3 = param_3 + 1;
          param_1 = param_1 + 1;
        }
      }
    }
  }
  return;
}



// ==== FUN_1000_5f90 @ 1000:5f90 ====

undefined2 __cdecl16near FUN_1000_5f90(void)

{
  return 0;
}



// ==== FUN_1000_644a @ 1000:644a ====

void __cdecl16near FUN_1000_644a(void)

{
  code *pcVar1;
  
  pcVar1 = (code *)swi(0x10);
  (*pcVar1)();
  return;
}



// ==== FUN_1000_6453 @ 1000:6453 ====

void __cdecl16near
FUN_1000_6453(byte *param_1,int param_2,undefined2 param_3,uint param_4,int param_5,
             undefined2 param_6)

{
  byte *pbVar1;
  byte *pbVar2;
  byte bVar3;
  uint uVar4;
  byte *pbVar5;
  int iVar6;
  int iVar7;
  uint uVar8;
  char cVar9;
  uint uVar10;
  undefined2 unaff_DS;
  undefined2 uVar11;
  
  while( true ) {
    pbVar1 = param_1 + 1;
    if (*param_1 == 0) break;
    uVar4 = (uint)*param_1 * 8;
    if (uVar4 < 0x400) {
      pbVar5 = (byte *)(uVar4 - 0x58b);
      uVar11 = 0xf000;
    }
    else {
      pbVar5 = (byte *)(uVar4 + 0x1b77);
      uVar11 = unaff_DS;
    }
    iVar7 = 8;
    do {
      pbVar2 = pbVar5;
      pbVar5 = pbVar5 + -1;
      bVar3 = *pbVar2;
      iVar7 = iVar7 + -1;
    } while (iVar7 != 0);
    *(int *)0x1f90 = param_2;
    *(undefined2 *)0x1f94 = param_3;
    uVar4 = 8;
    uVar10 = (uint)bVar3;
    do {
      uVar8 = uVar4;
      *(int *)0x1f96 = param_5 + -1 + *(int *)0x1f94;
      iVar7 = 8;
      do {
        cVar9 = (char)uVar10;
        iVar6 = (param_4 - 1) + *(int *)0x1f90;
        *(int *)0x1f92 = iVar6;
        if ((uVar10 & 0x80) != 0) {
          FUN_1000_6869(*(undefined2 *)0x1f90,*(undefined2 *)0x1f94,*(undefined2 *)0x1f92,
                        *(undefined2 *)0x1f96,param_6,pbVar5,uVar10,iVar7,param_1,iVar6);
        }
        *(int *)0x1f90 = *(int *)0x1f92 + 1;
        uVar10 = (uint)(byte)(cVar9 << 1 | cVar9 < '\0');
        iVar7 = iVar7 + -1;
      } while (iVar7 != 0);
      *(int *)0x1f90 = param_2;
      *(int *)0x1f94 = *(int *)0x1f96 + 1;
      uVar4 = uVar8 - 1;
      uVar10 = uVar8;
    } while (uVar4 != 0);
    param_2 = param_2 + (param_4 & 0xff) * 8;
    param_1 = pbVar1;
  }
  return;
}



// ==== FUN_1000_6524 @ 1000:6524 ====

void __cdecl16near FUN_1000_6524(char *param_1,undefined1 *param_2)

{
  undefined1 *puVar1;
  int iVar2;
  int iVar3;
  undefined1 *puVar4;
  undefined2 unaff_DS;
  
  if (*(uint *)0x266 != 0x140) {
    puVar1 = (undefined1 *)((*(uint *)0x266 >> 1) * *(int *)0x1fa0 + *(int *)0x26a);
    if ((*(uint *)0x266 & 1) != 0) {
      puVar1 = (undefined1 *)((uint)puVar1 ^ 0x2000);
    }
    iVar2 = 8;
    do {
      iVar3 = 3;
      puVar4 = puVar1;
      do {
        if (*param_1 == '\0') {
          *puVar4 = *param_2;
        }
        puVar4 = puVar4 + 1;
        param_1 = param_1 + 1;
        param_2 = param_2 + 1;
        iVar3 = iVar3 + -1;
      } while (iVar3 != 0);
      if (((uint)puVar1 & 0x2000) != 0) {
        puVar1 = puVar1 + 0x50;
      }
      puVar1 = (undefined1 *)((uint)puVar1 ^ 0x2000);
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
  }
  return;
}



// ==== FUN_1000_657c @ 1000:657c ====

void __cdecl16near FUN_1000_657c(byte *param_1,byte *param_2,byte *param_3)

{
  byte *pbVar1;
  byte *pbVar2;
  byte *pbVar3;
  byte *pbVar4;
  int iVar5;
  int iVar6;
  byte *pbVar7;
  undefined2 unaff_DS;
  
  if (*(uint *)0x260 != 0x140) {
    pbVar3 = (byte *)((*(uint *)0x260 >> 1) * *(int *)0x1fa0 + *(int *)0x268);
    if ((*(uint *)0x260 & 1) != 0) {
      pbVar3 = (byte *)((uint)pbVar3 ^ 0x2000);
    }
    iVar5 = 8;
    do {
      iVar6 = 3;
      pbVar4 = param_2;
      pbVar7 = pbVar3;
      do {
        pbVar1 = param_1;
        param_1 = param_1 + 1;
        param_2 = pbVar4 + 1;
        pbVar2 = param_3 + 1;
        *pbVar7 = *pbVar1 & *pbVar4 | *param_3;
        pbVar7 = pbVar7 + 1;
        iVar6 = iVar6 + -1;
        pbVar4 = param_2;
        param_3 = pbVar2;
      } while (iVar6 != 0);
      if (((uint)pbVar3 & 0x2000) != 0) {
        pbVar3 = pbVar3 + 0x50;
      }
      pbVar3 = (byte *)((uint)pbVar3 ^ 0x2000);
      iVar5 = iVar5 + -1;
    } while (iVar5 != 0);
  }
  return;
}



// ==== FUN_1000_65e0 @ 1000:65e0 ====

void __cdecl16near FUN_1000_65e0(void)

{
  code *pcVar1;
  
  pcVar1 = (code *)swi(0x10);
  (*pcVar1)();
  pcVar1 = (code *)swi(0x10);
  (*pcVar1)();
  return;
}



// ==== FUN_1000_6600 @ 1000:6600 ====

void __cdecl16near FUN_1000_6600(uint param_1,uint param_2,int param_3,uint param_4,int param_5)

{
  undefined1 *puVar1;
  undefined1 *puVar2;
  undefined1 *puVar3;
  uint uVar4;
  undefined1 *puVar5;
  undefined1 *puVar6;
  undefined1 *puVar7;
  undefined2 unaff_DS;
  
  if (param_2 != 0) {
    param_2 = param_2 - 1;
  }
  puVar3 = (undefined1 *)((param_1 >> 1) * *(int *)0x1fb0 + (param_2 >> 2));
  if ((param_1 & 1) != 0) {
    puVar3 = (undefined1 *)((uint)puVar3 ^ 0x2000);
  }
  puVar5 = puVar3 + -param_5;
  uVar4 = param_4 >> 2;
  puVar7 = puVar3;
  puVar6 = puVar5;
  do {
    for (; uVar4 != 0; uVar4 = uVar4 - 1) {
      puVar2 = puVar3;
      puVar3 = puVar3 + 1;
      puVar1 = puVar5;
      puVar5 = puVar5 + 1;
      *puVar2 = *puVar1;
    }
    if (0x1fff < (int)puVar6) {
      puVar6 = puVar6 + 0x50;
      puVar7 = puVar7 + 0x50;
    }
    puVar3 = (undefined1 *)((uint)puVar7 ^ 0x2000);
    puVar5 = (undefined1 *)((uint)puVar6 ^ 0x2000);
    param_3 = param_3 + -1;
    uVar4 = param_4 >> 2;
    puVar7 = puVar3;
    puVar6 = puVar5;
  } while (param_3 != 0);
  return;
}



// ==== FUN_1000_666a @ 1000:666a ====

int __cdecl16near FUN_1000_666a(char *param_1,char *param_2,int param_3)

{
  byte bVar1;
  char cVar2;
  undefined2 unaff_DS;
  int local_e;
  int local_c;
  int local_a;
  char *local_6;
  char *local_4;
  
  local_e = 0;
  local_a = 0;
  local_6 = param_1;
  local_4 = param_2;
  while (local_e < param_3) {
    if (*local_6 == -0x1c) {
      bVar1 = local_6[1];
      cVar2 = local_6[2];
      for (local_c = 0; local_c < (int)(uint)bVar1; local_c = local_c + 1) {
        *local_4 = cVar2;
        local_a = local_a + 1;
        local_4 = local_4 + 1;
      }
      local_e = local_e + 3;
      local_6 = local_6 + 3;
    }
    else {
      *local_4 = *local_6;
      local_a = local_a + 1;
      local_e = local_e + 1;
      local_6 = local_6 + 1;
      local_4 = local_4 + 1;
    }
  }
  return local_a;
}



// ==== FUN_1000_66fd @ 1000:66fd ====

void __cdecl16near FUN_1000_66fd(void)

{
  code *pcVar1;
  
  pcVar1 = (code *)swi(0x10);
  (*pcVar1)();
  return;
}



// ==== FUN_1000_672f @ 1000:672f ====

void __cdecl16near FUN_1000_672f(byte *param_1,uint param_2,uint param_3,int param_4,int param_5)

{
  byte *pbVar1;
  byte bVar2;
  byte *pbVar3;
  int iVar4;
  int iVar5;
  undefined2 unaff_DS;
  
  *(int *)0x2128 = param_2 + param_4;
  *(int *)0x2130 =
       ((int)((ulong)(long)(int)param_3 % (ulong)*(uint *)0x2120) +
       (int)((ulong)(long)param_5 % (ulong)*(uint *)0x2120)) * 2;
  *(uint *)0x2124 = param_3 >> 2;
  iVar4 = (int)((ulong)(long)(int)param_3 % (ulong)*(uint *)0x2120);
  *(int *)0x212c = iVar4 * 2;
  *(int *)0x212e = iVar4 * -2 + 8;
  iVar4 = (param_5 - 1U >> 2) + (param_3 >> 2);
  if (*(int *)0x212c != 0) {
    iVar4 = iVar4 + 1;
  }
LAB_1000_6797:
  if (*(int *)0x2128 <= (int)param_2) {
    return;
  }
  pbVar3 = (byte *)((param_2 >> 1) * *(int *)0x2122 + *(int *)0x2124);
  if ((param_2 & 1) != 0) {
    pbVar3 = pbVar3 + 0x2000;
  }
  for (iVar5 = *(int *)0x2124; iVar5 <= iVar4; iVar5 = iVar5 + 1) {
    if ((iVar5 == iVar4) && (*(int *)0x2130 != 0)) {
LAB_1000_680c:
      bVar2 = *param_1;
      param_1 = param_1 + 1;
      if (*(int *)0x212e < 8) {
        bVar2 = bVar2 << ((byte)*(undefined2 *)0x212e & 0x1f);
      }
      bVar2 = bVar2 | (byte)(*pbVar3 << ((byte)*(undefined2 *)0x2130 & 0x1f)) >>
                      ((byte)*(undefined2 *)0x2130 & 0x1f);
    }
    else {
      if (*(int *)0x212c == 0) goto LAB_1000_6834;
      if (iVar5 == *(int *)0x2124) {
        bVar2 = *param_1 >> ((byte)*(undefined2 *)0x212c & 0x1f) |
                (*pbVar3 >> ((byte)*(undefined2 *)0x212e & 0x1f)) <<
                ((byte)*(undefined2 *)0x212e & 0x1f);
      }
      else {
        if (iVar5 == iVar4) goto LAB_1000_680c;
        pbVar1 = param_1;
        param_1 = param_1 + 1;
        bVar2 = *pbVar1 << ((byte)*(undefined2 *)0x212e & 0x1f) |
                *param_1 >> ((byte)*(undefined2 *)0x212c & 0x1f);
      }
    }
    *pbVar3 = bVar2;
    pbVar3 = pbVar3 + 1;
  }
  goto LAB_1000_684b;
LAB_1000_6834:
  do {
    pbVar1 = param_1;
    param_1 = param_1 + 1;
    *pbVar3 = *pbVar1;
    pbVar3 = pbVar3 + 1;
    iVar5 = iVar5 + 1;
  } while (iVar5 <= iVar4);
LAB_1000_684b:
  param_2 = param_2 + 1;
  goto LAB_1000_6797;
}



// ==== FUN_1000_6853 @ 1000:6853 ====

undefined2 __cdecl16near FUN_1000_6853(int param_1)

{
  code *pcVar1;
  undefined2 uVar2;
  undefined1 in_ZF;
  
  pcVar1 = (code *)swi(0x16);
  uVar2 = (*pcVar1)();
  if (((bool)in_ZF) && (param_1 == 0x100)) {
    uVar2 = 0;
  }
  return uVar2;
}



// ==== FUN_1000_6869 @ 1000:6869 ====

void __cdecl16near FUN_1000_6869(uint param_1,uint param_2,uint param_3,int param_4,uint param_5)

{
  byte *pbVar1;
  byte bVar2;
  uint uVar3;
  byte bVar4;
  int iVar5;
  int iVar6;
  byte bVar7;
  uint uVar8;
  byte bVar9;
  int iVar10;
  byte *pbVar11;
  byte *pbVar12;
  undefined2 unaff_DS;
  
  pbVar11 = (byte *)((param_2 & 0xfe) * 8 + (CONCAT11((char)param_2,(char)param_2) & 0x1fe) * 0x20 +
                    ((int)param_1 >> 2));
  iVar5 = (param_4 - param_2) + 1;
  iVar10 = ((int)param_3 >> 2) - ((int)param_1 >> 2);
  bVar2 = *(byte *)((param_5 & 3) + 0x2160);
  uVar3 = *(uint *)(((param_1 & 3) * 4 + (param_3 & 3)) * 2 + 0x2140);
  uVar8 = CONCAT11(bVar2,bVar2) & uVar3;
  do {
    bVar4 = (byte)(uVar3 >> 8);
    bVar9 = (byte)(uVar8 >> 8);
    pbVar12 = pbVar11;
    if (iVar10 != 0) {
      pbVar12 = pbVar11 + 1;
      *pbVar11 = ~bVar4 & *pbVar11 | bVar9;
      iVar6 = iVar10 + -1;
      if (iVar6 != 0) {
        for (; iVar6 != 0; iVar6 = iVar6 + -1) {
          pbVar1 = pbVar12;
          pbVar12 = pbVar12 + 1;
          *pbVar1 = bVar2;
        }
      }
      bVar4 = 0xff;
    }
    bVar4 = bVar4 & (byte)uVar3;
    bVar7 = (byte)uVar8 & bVar4;
    uVar8 = CONCAT11(bVar9,bVar7);
    *pbVar12 = ~bVar4 & *pbVar12 | bVar7;
    if (((uint)pbVar11 & 0x2000) != 0) {
      pbVar11 = pbVar11 + 0x50;
    }
    pbVar11 = (byte *)((uint)pbVar11 ^ 0x2000);
    iVar5 = iVar5 + -1;
  } while (iVar5 != 0);
  return;
}



// ==== FUN_1000_6939 @ 1000:6939 ====

void __cdecl16near FUN_1000_6939(uint param_1,uint param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  undefined2 unaff_DS;
  
  iVar1 = (param_1 >> 1 & 0xff) * (uint)*(byte *)0x2170 + (param_2 >> 2);
  *(int *)0x2176 = iVar1;
  *(int *)0x2174 = iVar1 + 0x2000;
  if ((param_1 & 1) != 0) {
    *(int *)0x2176 = *(int *)0x2176 + 0x50;
  }
  iVar1 = 8;
  do {
    if ((param_1 & 1) == 0) {
      iVar4 = *(int *)0x2176;
      *(int *)0x2176 = *(int *)0x2176 + *(int *)0x2171;
    }
    else {
      iVar4 = *(int *)0x2174;
      *(int *)0x2174 = *(int *)0x2174 + *(int *)0x2171;
    }
    iVar3 = 0;
    iVar2 = 3;
    do {
      *(undefined1 *)(iVar3 + param_3) = *(undefined1 *)(iVar3 + iVar4);
      iVar3 = iVar3 + 1;
      iVar2 = iVar2 + -1;
    } while (iVar2 != 0);
    param_3 = param_3 + 3;
    param_1 = param_1 + 1;
    iVar1 = iVar1 + -1;
  } while (iVar1 != 0);
  return;
}



// ==== FUN_1000_6a48 @ 1000:6a48 ====

void __cdecl16near FUN_1000_6a48(char *param_1)

{
  int iVar1;
  char cVar2;
  undefined1 *puVar3;
  char *pcVar4;
  char *pcVar5;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  int local_10c;
  int local_108;
  char *local_106;
  undefined1 *local_104;
  undefined1 local_102 [256];
  
  local_104 = &stack0x0004;
  while (*param_1 != '\0') {
    pcVar5 = param_1 + 1;
    cVar2 = *param_1;
    if (cVar2 == '%') {
      if (*pcVar5 == '%') {
        cVar2 = *pcVar5;
        iVar1 = *(int *)0x22ec;
        *(int *)0x22ec = iVar1 + -1;
        if (iVar1 + -1 < 0) {
          FUN_1000_7d68(cVar2,0x22ea);
          param_1 = param_1 + 2;
        }
        else {
          pcVar5 = (char *)*(undefined2 *)0x22ea;
          *(int *)0x22ea = *(int *)0x22ea + 1;
          *pcVar5 = cVar2;
          param_1 = param_1 + 2;
        }
      }
      else {
        pcVar4 = (char *)FUN_1000_7eba(pcVar5,local_102,&local_104,&local_108,param_1);
        param_1 = pcVar5;
        local_106 = pcVar4;
        if (pcVar4 != (char *)0x0) {
          for (local_10c = 0; param_1 = pcVar4, local_10c < local_108; local_10c = local_10c + 1) {
            iVar1 = *(int *)0x22ec;
            *(int *)0x22ec = iVar1 + -1;
            if (iVar1 + -1 < 0) {
              FUN_1000_7d68(local_102[local_10c],0x22ea);
            }
            else {
              puVar3 = (undefined1 *)*(undefined2 *)0x22ea;
              *(int *)0x22ea = *(int *)0x22ea + 1;
              *puVar3 = local_102[local_10c];
            }
          }
        }
      }
    }
    else {
      iVar1 = *(int *)0x22ec;
      *(int *)0x22ec = iVar1 + -1;
      if (iVar1 + -1 < 0) {
        FUN_1000_7d68(cVar2,0x22ea);
        param_1 = pcVar5;
      }
      else {
        pcVar4 = (char *)*(undefined2 *)0x22ea;
        *(int *)0x22ea = *(int *)0x22ea + 1;
        *pcVar4 = cVar2;
        param_1 = pcVar5;
      }
    }
  }
  return;
}



// ==== FUN_1000_6b57 @ 1000:6b57 ====

int __cdecl16near FUN_1000_6b57(undefined2 param_1,uint param_2)

{
  int iVar1;
  undefined2 unaff_DS;
  undefined2 local_6;
  undefined2 local_4;
  
  local_6 = 0;
  while ((local_6 < 0x10 && ((*(uint *)(local_6 * 0xc + 0x2178) & 0x8000) != 0))) {
    local_6 = local_6 + 1;
  }
  if (local_6 == 0x10) {
    *(undefined2 *)0x2238 = 0x17;
    return -1;
  }
  iVar1 = FUN_1000_777a(param_1,local_6 * 0xc + 0x217a);
  if (iVar1 != 0) {
    *(undefined2 *)0x2238 = 2;
    return -1;
  }
  local_4 = 0xd;
  if ((param_2 & 0x8000) != 0) {
    local_4 = 0x10d;
  }
  iVar1 = FUN_1000_78e3(local_6,local_4,local_6 * 0xc + 0x217a);
  *(int *)0x223a = iVar1;
  if (iVar1 != 0) {
    *(undefined2 *)0x2238 = 5;
    return -1;
  }
  FUN_1000_78e3(local_6,4);
  local_4 = 0x8000;
  if ((param_2 & 0x8000) != 0) {
    local_4 = 0x9000;
    param_2 = param_2 & 0x7fff;
  }
  if (param_2 == 0) {
    local_4 = local_4 | 0x4000;
  }
  else if (param_2 == 1) {
    local_4 = local_4 | 0x2000;
  }
  *(uint *)(local_6 * 0xc + 0x2178) = local_4;
  return local_6;
}



// ==== FUN_1000_6c51 @ 1000:6c51 ====

int __cdecl16near FUN_1000_6c51(undefined2 param_1,uint param_2)

{
  uint *puVar1;
  int iVar2;
  undefined2 unaff_DS;
  undefined2 local_6;
  undefined2 local_4;
  
  local_6 = 0;
  while ((local_6 < 0x10 && ((*(uint *)(local_6 * 0xc + 0x2178) & 0x8000) != 0))) {
    local_6 = local_6 + 1;
  }
  if (local_6 == 0x10) {
    *(undefined2 *)0x2238 = 0x17;
    return -1;
  }
  iVar2 = FUN_1000_7768(param_1,param_2,local_6 * 0xc + 0x217a);
  if (iVar2 != 0) {
    *(undefined2 *)0x2238 = 0;
    return -1;
  }
  local_4 = 0xd;
  if ((param_2 & 0x8000) != 0) {
    local_4 = 0x10d;
  }
  iVar2 = FUN_1000_78e3(local_6,local_4,local_6 * 0xc + 0x217a);
  *(int *)0x223a = iVar2;
  if (iVar2 != 0) {
    *(undefined2 *)0x2238 = 5;
    return -1;
  }
  FUN_1000_78e3(local_6,4);
  *(undefined2 *)(local_6 * 0xc + 0x2178) = 0x8000;
  if ((param_2 & 0x8000) != 0) {
    puVar1 = (uint *)(local_6 * 0xc + 0x2178);
    *puVar1 = *puVar1 | 0x1000;
  }
  return local_6;
}



// ==== FUN_1000_6d31 @ 1000:6d31 ====

undefined2 __cdecl16near FUN_1000_6d31(int param_1,undefined2 param_2,undefined2 param_3)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined2 unaff_DS;
  undefined2 local_4;
  
  if ((param_1 < 0) || (0xf < param_1)) {
    *(undefined2 *)0x2238 = 9;
    return 0xffff;
  }
  iVar2 = param_1 * 0xc;
  uVar1 = *(uint *)(iVar2 + 0x2178);
  if (((uVar1 & 0x8000) != 0) && ((uVar1 & 0x2000) == 0)) {
    *(undefined2 *)(iVar2 + 0x217e) = param_3;
    *(undefined2 *)(iVar2 + 0x2182) = param_2;
    local_4 = 0x3001;
    if ((*(uint *)(iVar2 + 0x2178) & 0x1000) != 0) {
      local_4 = 0x3101;
    }
    iVar3 = FUN_1000_78e3(param_1,local_4,iVar2 + 0x217e);
    *(int *)0x223a = iVar3;
    if (iVar3 == 1) {
      return 0;
    }
    if (*(int *)0x223a != 0) {
      *(undefined2 *)0x2238 = 5;
      return 0xffff;
    }
    return *(undefined2 *)(iVar2 + 0x2180);
  }
  *(undefined2 *)0x2238 = 9;
  return 0xffff;
}



// ==== FUN_1000_6ddd @ 1000:6ddd ====

undefined2 __cdecl16near FUN_1000_6ddd(int param_1,undefined2 param_2,undefined2 param_3)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined2 unaff_DS;
  undefined2 local_4;
  
  if ((param_1 < 0) || (0xf < param_1)) {
    *(undefined2 *)0x2238 = 9;
    return 0xffff;
  }
  iVar2 = param_1 * 0xc;
  uVar1 = *(uint *)(iVar2 + 0x2178);
  if (((uVar1 & 0x8000) != 0) && ((uVar1 & 0x4000) == 0)) {
    *(undefined2 *)(iVar2 + 0x217e) = param_3;
    *(undefined2 *)(iVar2 + 0x2182) = param_2;
    local_4 = 0x3002;
    if ((*(uint *)(iVar2 + 0x2178) & 0x1000) != 0) {
      local_4 = 0x3102;
    }
    iVar3 = FUN_1000_78e3(param_1,local_4,iVar2 + 0x217e);
    *(int *)0x223a = iVar3;
    if (iVar3 == -0x7fff) {
      return 0;
    }
    if (*(int *)0x223a != 0) {
      *(undefined2 *)0x2238 = 5;
      return 0xffff;
    }
    return *(undefined2 *)(iVar2 + 0x2180);
  }
  *(undefined2 *)0x2238 = 9;
  return 0xffff;
}



// ==== FUN_1000_6e8b @ 1000:6e8b ====

/* WARNING: Removing unreachable block (ram,0x00016edf) */

int __cdecl16near FUN_1000_6e8b(int param_1,uint param_2,int param_3,int param_4)

{
  undefined2 uVar1;
  int iVar2;
  undefined2 unaff_DS;
  bool bVar3;
  uint local_6;
  int local_4;
  
  if ((param_1 < 0) || (0xf < param_1)) {
    *(undefined2 *)0x2238 = 9;
    return -1;
  }
  if ((*(uint *)(param_1 * 0xc + 0x2178) & 0x8000) == 0) {
    *(undefined2 *)0x2238 = 9;
    return -1;
  }
  if (param_4 == 2) {
    uVar1 = FUN_1000_78e3(param_1,0x2108,&local_6);
    *(undefined2 *)0x223a = uVar1;
  }
  else if (param_4 == 1) {
    uVar1 = FUN_1000_78e3(param_1,0x2008,&local_6);
    *(undefined2 *)0x223a = uVar1;
  }
  else {
    if (param_4 != 0) {
      *(undefined2 *)0x2238 = 0x16;
      return -1;
    }
    local_6 = 0;
    *(undefined2 *)0x223a = 0;
    local_4 = 0;
  }
  if (*(int *)0x223a == 0) {
    bVar3 = CARRY2(param_2,local_6);
    param_2 = param_2 + local_6;
    param_3 = param_3 + local_4 + (uint)bVar3;
    iVar2 = FUN_1000_78e3(param_1,0x2000,&param_2);
    *(int *)0x223a = iVar2;
    if (iVar2 != 0) {
      *(undefined2 *)0x2238 = 5;
      return -1;
    }
    iVar2 = FUN_1000_78e3(param_1,8,&param_2);
    *(int *)0x223a = iVar2;
    if (iVar2 == 0) {
      return param_3;
    }
    *(undefined2 *)0x2238 = 5;
    return -1;
  }
  *(undefined2 *)0x2238 = 5;
  return -1;
}



// ==== FUN_1000_6fb6 @ 1000:6fb6 ====

long __cdecl16near FUN_1000_6fb6(int param_1)

{
  int iVar1;
  int iVar2;
  undefined2 in_DX;
  uint uVar3;
  undefined2 unaff_DS;
  
  if ((param_1 < 0) || (0xf < param_1)) {
    *(undefined2 *)0x2238 = 9;
    return CONCAT22(in_DX,0xffff);
  }
  if ((*(uint *)((int)((long)param_1 * 0xc) + 0x2178) & 0x8000) == 0) {
    *(undefined2 *)0x2238 = 9;
    return CONCAT22((int)((ulong)((long)param_1 * 0xc) >> 0x10),0xffff);
  }
  iVar1 = FUN_1000_78e3(param_1,5);
  iVar2 = FUN_1000_78e3(param_1,0xe);
  uVar3 = (uint)((ulong)((long)param_1 * 0xc) >> 0x10);
  *(undefined2 *)((int)((long)param_1 * 0xc) + 0x2178) = 0;
  if ((iVar1 == 0) && (iVar2 == 0)) {
    return (ulong)uVar3 << 0x10;
  }
  return CONCAT22(uVar3,0xffff);
}



// ==== FUN_1000_7040 @ 1000:7040 ====

uint __cdecl16near FUN_1000_7040(void)

{
  uint in_AX;
  uint uVar1;
  uint in_CX;
  uint in_DX;
  int in_BX;
  uint uVar2;
  uint uVar3;
  int iVar4;
  bool bVar5;
  bool bVar6;
  
  if (in_CX == 0 && in_DX == 0) {
    uVar1 = 0;
  }
  else if (in_AX == 0 && in_BX == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = in_AX;
    if ((int)in_AX < 0) {
      bVar5 = in_BX != 0;
      in_BX = -in_BX;
      uVar1 = (~in_AX + 1) - (uint)bVar5;
    }
    uVar2 = in_AX ^ in_CX;
    uVar3 = 0;
    if ((int)in_CX < 0) {
      bVar5 = in_DX != 0;
      in_DX = -in_DX;
      in_CX = (~in_CX + 1) - (uint)bVar5;
    }
    if ((in_CX == 0) && (-1 < (int)in_DX)) {
      iVar4 = 0x20;
      do {
        bVar5 = in_BX < 0;
        in_BX = in_BX * 2;
        bVar6 = (int)uVar1 < 0;
        uVar1 = uVar1 << 1 | (uint)bVar5;
        uVar3 = uVar3 << 1 | (uint)bVar6;
        if (in_DX <= uVar3) {
          uVar3 = uVar3 - in_DX;
          in_BX = in_BX + 1;
        }
        iVar4 = iVar4 + -1;
      } while (iVar4 != 0);
    }
    else {
      iVar4 = 0x10;
      do {
        bVar5 = in_BX < 0;
        in_BX = in_BX * 2;
        bVar6 = (int)uVar1 < 0;
        uVar1 = uVar1 << 1 | (uint)bVar5;
        uVar3 = uVar3 << 1 | (uint)bVar6;
        if ((in_CX <= uVar3) && ((uVar3 != in_CX || (in_DX <= uVar1)))) {
          bVar5 = uVar1 < in_DX;
          uVar1 = uVar1 - in_DX;
          uVar3 = (uVar3 - in_CX) - (uint)bVar5;
          in_BX = in_BX + 1;
        }
        iVar4 = iVar4 + -1;
      } while (iVar4 != 0);
      uVar1 = 0;
    }
    if ((uVar2 & 0x8000) != 0) {
      uVar1 = (~uVar1 + 1) - (uint)(in_BX != 0);
    }
  }
  return uVar1;
}



// ==== FUN_1000_70e8 @ 1000:70e8 ====

void __cdecl16near FUN_1000_70e8(byte *param_1)

{
  byte bVar1;
  byte *pbVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined2 unaff_DS;
  int local_a;
  
  while ((*(byte *)(*param_1 + 0x2363) & 8) != 0) {
    param_1 = param_1 + 1;
  }
  *(undefined2 *)0x2240 = 0;
  do {
    if (0x1f < *(int *)0x2240) break;
    bVar1 = *param_1;
    if (bVar1 == 0x3e) {
      pbVar2 = param_1 + 1;
      if (param_1[1] == 0x3e) {
        *(undefined2 *)0x2244 = 0x22aa;
        pbVar2 = param_1 + 2;
      }
      param_1 = pbVar2;
      local_a = 0;
      while ((*param_1 != 0 && ((*(byte *)(*param_1 + 0x2363) & 8) == 0))) {
        if (local_a < 0x10) {
          *(byte *)(local_a + 0x2257) = *param_1;
          local_a = local_a + 1;
        }
        param_1 = param_1 + 1;
      }
      *(undefined1 *)(local_a + 0x2257) = 0;
    }
    else if (bVar1 == 0x3c) {
      local_a = 0;
      while( true ) {
        param_1 = param_1 + 1;
        if ((*param_1 == 0) || ((*(byte *)(*param_1 + 0x2363) & 8) != 0)) break;
        if (local_a < 0x10) {
          *(byte *)(local_a + 0x2246) = *param_1;
          local_a = local_a + 1;
        }
      }
      *(undefined1 *)(local_a + 0x2246) = 0;
    }
    else if (bVar1 == 0x3d) {
      *(undefined2 *)0x2494 = 0;
      while (param_1 = param_1 + 1, (*(byte *)(*param_1 + 0x2363) & 4) != 0) {
        *(int *)0x2494 = *(int *)0x2494 * 10 + (*param_1 & 0xf);
      }
    }
    else {
      iVar3 = *(int *)0x2240;
      *(int *)0x2240 = *(int *)0x2240 + 1;
      *(undefined2 *)(iVar3 * 2 + 0x226a) = param_1;
      while ((*param_1 != 0 && ((*(byte *)(*param_1 + 0x2363) & 8) == 0))) {
        param_1 = param_1 + 1;
      }
    }
    bVar1 = *param_1;
    *param_1 = 0;
    if (bVar1 == 0) break;
    do {
      param_1 = param_1 + 1;
    } while ((*(byte *)(*param_1 + 0x2363) & 8) != 0);
  } while (*param_1 != 0);
  iVar3 = FUN_1000_7539(0x2246,0x22ac);
  iVar4 = FUN_1000_7539(0x2257,*(undefined2 *)0x2244);
  iVar5 = FUN_1000_7539(0x2268,0x22aa);
  if (iVar5 == 0) {
    FUN_1000_7701(1);
  }
  if (iVar3 == 0) {
    FUN_1000_86b3(0x22ae,iVar5);
    FUN_1000_7711(1);
  }
  if (iVar4 == 0) {
    FUN_1000_86b3(0x22c5,iVar5);
    FUN_1000_7711(1);
  }
  if (*(char *)0x2246 == '\0') {
    *(byte *)(iVar3 + 6) = *(byte *)(iVar3 + 6) | 4;
  }
  if (*(char *)0x2257 == '\0') {
    *(byte *)(iVar4 + 6) = *(byte *)(iVar4 + 6) | 4;
  }
  *(byte *)(iVar5 + 6) = *(byte *)(iVar5 + 6) | 4;
  FUN_1000_0082(*(undefined2 *)0x2240,0x226a);
  FUN_1000_7711(0);
  return;
}



// ==== FUN_1000_735a @ 1000:735a ====

byte __cdecl16near FUN_1000_735a(void)

{
  byte bVar1;
  undefined2 unaff_DS;
  
  bVar1 = *(byte *)0x22e0;
  if (bVar1 != 0) {
    *(undefined1 *)0x22e0 = 0;
    return bVar1;
  }
  bVar1 = FUN_1000_7757(7,0xff,0);
  return bVar1 & 0x7f;
}



// ==== FUN_1000_7443 @ 1000:7443 ====

bool __cdecl16near FUN_1000_7443(void)

{
  int iVar1;
  
  iVar1 = FUN_1000_7757(0xb);
  return iVar1 != 0;
}



// ==== FUN_1000_7464 @ 1000:7464 ====

int __cdecl16near FUN_1000_7464(char *param_1,char *param_2)

{
  char *pcVar1;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  int local_10e;
  int local_10a;
  char *local_108;
  char *local_106;
  undefined1 *local_104;
  char local_102 [256];
  
  local_104 = &stack0x0006;
  local_106 = param_1;
  while (*param_2 != '\0') {
    pcVar1 = param_2 + 1;
    if (*param_2 == '%') {
      if (*pcVar1 == '%') {
        *param_1 = *pcVar1;
        param_1 = param_1 + 1;
        param_2 = param_2 + 2;
      }
      else {
        local_108 = (char *)FUN_1000_7eba(pcVar1,local_102,&local_104,&local_10a,param_2);
        param_2 = pcVar1;
        if (local_108 != (char *)0x0) {
          for (local_10e = 0; param_2 = local_108, local_10e < local_10a; local_10e = local_10e + 1)
          {
            *param_1 = local_102[local_10e];
            param_1 = param_1 + 1;
          }
        }
      }
    }
    else {
      *param_1 = *param_2;
      param_1 = param_1 + 1;
      param_2 = pcVar1;
    }
  }
  *param_1 = '\0';
  return (int)param_1 - (int)local_106;
}



// ==== FUN_1000_751c @ 1000:751c ====

undefined2 __cdecl16near FUN_1000_751c(void)

{
  undefined2 in_AX;
  
  return in_AX;
}



// ==== FUN_1000_7539 @ 1000:7539 ====

undefined2 __cdecl16near FUN_1000_7539(undefined2 param_1,undefined2 param_2)

{
  undefined2 uVar1;
  undefined2 unaff_DS;
  undefined2 local_6;
  
  for (local_6 = 0x22e2; (local_6 < 0x2362 && (*(char *)(local_6 + 6) != '\0'));
      local_6 = local_6 + 8) {
  }
  if (local_6 == 0x2362) {
    return 0;
  }
  uVar1 = FUN_1000_7580(param_1,param_2,local_6);
  return uVar1;
}



// ==== FUN_1000_7580 @ 1000:7580 ====

int * __cdecl16near FUN_1000_7580(char *param_1,char *param_2,int *param_3)

{
  char cVar1;
  byte bVar2;
  undefined2 unaff_DS;
  int local_6;
  int local_4;
  
  if (*(byte *)(param_3 + 3) != 0) {
    if ((*(byte *)(param_3 + 3) & 2) != 0) {
      FUN_1000_7d68(0xffff,param_3);
    }
    FUN_1000_6fb6(*(undefined1 *)((int)param_3 + 7));
  }
  cVar1 = *param_2;
  if (cVar1 == 'w') {
    local_6 = FUN_1000_6c51(param_1,*(int *)0x2548 + 0x1a4);
    bVar2 = 2;
  }
  else if (cVar1 == 'r') {
    local_6 = FUN_1000_6b57(param_1,*(undefined2 *)0x2548);
    bVar2 = 1;
  }
  else {
    if (cVar1 != 'a') {
      return (int *)0x0;
    }
    local_6 = FUN_1000_6b57(param_1,*(int *)0x2548 + 1);
    if (local_6 == -1) {
      local_6 = FUN_1000_6c51(param_1,*(int *)0x2548 + 0x1a4);
    }
    FUN_1000_6e8b(local_6,0,0,2);
    bVar2 = 2;
  }
  if (local_6 == -1) {
    return (int *)0x0;
  }
  local_4 = param_3[2];
  if (local_4 == 0) {
    local_4 = FUN_1000_88ef(0x200);
    if (local_4 == 0) {
      FUN_1000_6fb6(local_6);
      return (int *)0x0;
    }
  }
  if (*param_1 == '\0') {
    bVar2 = bVar2 | 4;
  }
  *(undefined1 *)((int)param_3 + 7) = (char)local_6;
  *param_3 = local_4;
  param_3[2] = local_4;
  *(byte *)(param_3 + 3) = bVar2;
  if ((bVar2 & 5) == 0) {
    param_3[1] = 0x200;
  }
  else {
    param_3[1] = 0;
  }
  return param_3;
}



// ==== FUN_1000_76b9 @ 1000:76b9 ====

void __cdecl16near FUN_1000_76b9(int param_1)

{
  undefined2 unaff_DS;
  
  if ((*(byte *)(param_1 + 6) & 2) != 0) {
    FUN_1000_7d68(0xffff,param_1);
  }
  FUN_1000_898f(*(undefined2 *)(param_1 + 4),0x200);
  *(undefined2 *)(param_1 + 4) = 0;
  *(undefined1 *)(param_1 + 6) = 0;
  FUN_1000_6fb6(*(undefined1 *)(param_1 + 7));
  return;
}



// ==== FUN_1000_7701 @ 1000:7701 ====

void __cdecl16near FUN_1000_7701(undefined2 param_1,undefined2 param_2)

{
  FUN_1000_0079(param_2);
  return;
}



// ==== FUN_1000_7711 @ 1000:7711 ====

void __cdecl16near FUN_1000_7711(undefined2 param_1,undefined2 param_2)

{
  int iVar1;
  undefined2 unaff_DS;
  undefined2 local_4;
  
  for (local_4 = 0; local_4 < 0x10; local_4 = local_4 + 1) {
    iVar1 = local_4 * 8;
    if ((*(byte *)(iVar1 + 0x22e8) & 2) != 0) {
      FUN_1000_76b9(iVar1 + 0x22e2,iVar1);
    }
  }
  FUN_1000_7701(param_1,param_2);
  return;
}



// ==== FUN_1000_7757 @ 1000:7757 ====

void __cdecl16near FUN_1000_7757(void)

{
  code *pcVar1;
  
  pcVar1 = (code *)swi(0x21);
  (*pcVar1)();
  return;
}



// ==== FUN_1000_7768 @ 1000:7768 ====

undefined2 __cdecl16near FUN_1000_7768(undefined2 param_1,undefined2 param_2,undefined2 *param_3)

{
  code *pcVar1;
  undefined2 *puVar2;
  char cVar3;
  byte *pbVar4;
  undefined2 uVar5;
  undefined2 unaff_DS;
  
  param_2 = param_3;
  pbVar4 = (byte *)FUN_1000_86ff(param_1);
  puVar2 = param_2;
  if (pbVar4 == (byte *)0x0) {
    uVar5 = 0xffff;
  }
  else {
    if ((*pbVar4 & 0x80) == 0) {
      pcVar1 = (code *)swi(0x21);
      cVar3 = (*pcVar1)();
      if (cVar3 != '\0') {
        FUN_1000_88c4(pbVar4);
        return 0xffff;
      }
    }
    *puVar2 = pbVar4;
    uVar5 = 0;
  }
  return uVar5;
}



// ==== FUN_1000_777a @ 1000:777a ====

undefined2 __cdecl16near FUN_1000_777a(undefined2 param_1,undefined2 *param_2)

{
  code *pcVar1;
  char cVar2;
  byte *pbVar3;
  undefined2 uVar4;
  undefined2 unaff_DS;
  
  pbVar3 = (byte *)FUN_1000_86ff(param_1);
  if (pbVar3 == (byte *)0x0) {
    uVar4 = 0xffff;
  }
  else {
    if ((*pbVar3 & 0x80) == 0) {
      pcVar1 = (code *)swi(0x21);
      cVar2 = (*pcVar1)();
      if (cVar2 != '\0') {
        FUN_1000_88c4(pbVar3);
        return 0xffff;
      }
    }
    *param_2 = pbVar3;
    uVar4 = 0;
  }
  return uVar4;
}



// ==== FUN_1000_77be @ 1000:77be ====

undefined2 __cdecl16near FUN_1000_77be(undefined2 param_1)

{
  code *pcVar1;
  char cVar2;
  byte *pbVar3;
  undefined2 unaff_DS;
  
  pbVar3 = (byte *)FUN_1000_86ff(param_1);
  if (pbVar3 == (byte *)0x0) {
    return 0xffff;
  }
  if ((*pbVar3 & 0x80) == 0) {
    pcVar1 = (code *)swi(0x21);
    cVar2 = (*pcVar1)();
    if (cVar2 != '\0') {
      FUN_1000_88c4();
      return 0xffff;
    }
    FUN_1000_88c4();
  }
  return 0;
}



// ==== FUN_1000_77f8 @ 1000:77f8 ====

undefined4 __cdecl16near FUN_1000_77f8(void)

{
  int iVar1;
  uint uVar2;
  uint in_AX;
  int iVar3;
  uint in_DX;
  int in_BX;
  uint uVar4;
  undefined2 unaff_DS;
  
  iVar3 = 7;
  iVar1 = *(int *)(in_BX + 0x2e);
  if (((iVar1 != 0x80) && (iVar3 = 8, iVar1 != 0x100)) && (iVar3 = 9, iVar1 != 0x200)) {
    iVar3 = 10;
  }
  uVar4 = iVar1 - 1U & in_DX;
  do {
    uVar2 = in_AX & 1;
    in_AX = in_AX >> 1;
    in_DX = in_DX >> 1 | (uint)(uVar2 != 0) << 0xf;
    iVar3 = iVar3 + -1;
  } while (iVar3 != 0);
  return CONCAT22(uVar4,in_DX);
}



// ==== FUN_1000_7825 @ 1000:7825 ====

undefined4 __cdecl16near FUN_1000_7825(void)

{
  int iVar1;
  int in_AX;
  int iVar2;
  uint uVar3;
  int in_BX;
  undefined2 unaff_DS;
  bool bVar4;
  
  iVar2 = 7;
  iVar1 = *(int *)(in_BX + 0x2e);
  if (((iVar1 != 0x80) && (iVar2 = 8, iVar1 != 0x100)) && (iVar2 = 9, iVar1 != 0x200)) {
    iVar2 = 10;
  }
  uVar3 = 0;
  do {
    bVar4 = in_AX < 0;
    in_AX = in_AX << 1;
    uVar3 = uVar3 << 1 | (uint)bVar4;
    iVar2 = iVar2 + -1;
  } while (iVar2 != 0);
  return CONCAT22(in_AX,uVar3);
}



// ==== FUN_1000_784e @ 1000:784e ====

void __cdecl16near FUN_1000_784e(void)

{
  code *pcVar1;
  int in_BX;
  int unaff_BP;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  undefined4 uVar2;
  
  *(undefined1 *)(unaff_BP + 3) = 0x27;
  if (*(int *)(in_BX + 0x30) == *(int *)(in_BX + 0x2e)) {
    *(int *)(in_BX + 0xe) = *(int *)(in_BX + 0x30);
    *(undefined2 *)(in_BX + 0x21) = *(undefined2 *)(in_BX + 0x32);
    *(undefined2 *)(in_BX + 0x23) = 0;
  }
  else {
    *(undefined2 *)(in_BX + 0xe) = 1;
    uVar2 = FUN_1000_7825();
    *(undefined2 *)(in_BX + 0x21) = (int)((ulong)uVar2 >> 0x10);
    *(undefined2 *)(in_BX + 0x23) = (int)uVar2;
  }
  pcVar1 = (code *)swi(0x21);
  (*pcVar1)();
  pcVar1 = (code *)swi(0x21);
  (*pcVar1)();
  return;
}



// ==== FUN_1000_7854 @ 1000:7854 ====

void __cdecl16near FUN_1000_7854(void)

{
  code *pcVar1;
  int in_BX;
  int unaff_BP;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  undefined4 uVar2;
  
  *(undefined1 *)(unaff_BP + 3) = 0x28;
  if (*(int *)(in_BX + 0x30) == *(int *)(in_BX + 0x2e)) {
    *(int *)(in_BX + 0xe) = *(int *)(in_BX + 0x30);
    *(undefined2 *)(in_BX + 0x21) = *(undefined2 *)(in_BX + 0x32);
    *(undefined2 *)(in_BX + 0x23) = 0;
  }
  else {
    *(undefined2 *)(in_BX + 0xe) = 1;
    uVar2 = FUN_1000_7825();
    *(undefined2 *)(in_BX + 0x21) = (int)((ulong)uVar2 >> 0x10);
    *(undefined2 *)(in_BX + 0x23) = (int)uVar2;
  }
  pcVar1 = (code *)swi(0x21);
  (*pcVar1)();
  pcVar1 = (code *)swi(0x21);
  (*pcVar1)();
  return;
}



// ==== FUN_1000_789e @ 1000:789e ====

undefined2 __cdecl16near FUN_1000_789e(void)

{
  uint in_AX;
  int iVar1;
  undefined2 uVar2;
  int in_BX;
  int unaff_BP;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  
  if (in_AX == *(uint *)(in_BX + 0x32)) {
    return 0;
  }
  if (*(char *)(in_BX + 0x25) != '\0') {
    iVar1 = FUN_1000_7854();
    if (iVar1 != 0) {
      return 0xffff;
    }
  }
  *(undefined1 *)(in_BX + 0x25) = 0;
  *(uint *)(in_BX + 0x32) = in_AX;
  if (in_AX < *(uint *)(unaff_BP + 6)) {
    *(undefined2 *)(in_BX + 0x30) = *(undefined2 *)(in_BX + 0x2e);
  }
  else {
    if (in_AX != *(uint *)(unaff_BP + 6)) {
      *(undefined2 *)(in_BX + 0x30) = 0;
      return 0;
    }
    iVar1 = *(int *)(unaff_BP + 8);
    *(int *)(in_BX + 0x30) = iVar1;
    if (iVar1 == 0) {
      return 0;
    }
  }
  uVar2 = FUN_1000_784e();
  return uVar2;
}



// ==== FUN_1000_78e3 @ 1000:78e3 ====

undefined2 __cdecl16near FUN_1000_78e3(int param_1,uint param_2,uint *param_3)

{
  uint *puVar1;
  byte *pbVar2;
  char *pcVar3;
  byte *pbVar4;
  code *pcVar5;
  byte in_AL;
  char cVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int extraout_DX;
  int extraout_DX_00;
  uint uVar10;
  int extraout_DX_01;
  byte *in_BX;
  uint uVar11;
  byte *pbVar12;
  int iVar13;
  char *pcVar14;
  char *pcVar15;
  char *pcVar16;
  byte *pbVar17;
  byte *pbVar18;
  uint *unaff_DI;
  undefined2 unaff_ES;
  undefined2 unaff_DS;
  undefined4 uVar19;
  byte bVar20;
  byte bVar21;
  uint local_4;
  
  uVar11 = param_2 & 0xf;
  if (uVar11 != 0xd) {
    unaff_DI = (uint *)(param_1 * 2);
    in_BX = (byte *)unaff_DI[0x1232];
    in_AL = *in_BX;
  }
  if (uVar11 == 0) {
    if ((in_AL & 0x80) == 0) {
      uVar11 = param_3[1];
      if ((uVar11 < *(uint *)(in_BX + 0x2c)) ||
         ((uVar11 == *(uint *)(in_BX + 0x2c) && (*param_3 <= *(uint *)(in_BX + 0x2a))))) {
        uVar7 = *param_3;
        *(uint *)(in_BX + 0x28) = uVar11;
        *(uint *)(in_BX + 0x26) = uVar7;
        return 0;
      }
    }
    return 0xffff;
  }
  if (uVar11 == 1) {
    if ((in_AL & 0x80) == 0) {
      uVar11 = *param_3;
      if ((int)uVar11 < 0) {
        return 0xffff;
      }
      if (uVar11 == 0) {
        return 1;
      }
      uVar7 = *(int *)(in_BX + 0x28) + (uint)CARRY2(*(uint *)(in_BX + 0x26),uVar11);
      if ((*(uint *)(in_BX + 0x2c) <= uVar7) &&
         ((uVar7 != *(uint *)(in_BX + 0x2c) ||
          (*(uint *)(in_BX + 0x2a) < *(uint *)(in_BX + 0x26) + uVar11)))) {
        uVar11 = *(int *)(in_BX + 0x2a) - *(int *)(in_BX + 0x26);
      }
      param_3[1] = uVar11;
      FUN_1000_77f8();
      pbVar18 = (byte *)param_3[2];
      FUN_1000_77f8();
      iVar13 = extraout_DX;
      while( true ) {
        iVar8 = FUN_1000_789e();
        if (iVar8 != 0) {
          return 0xffff;
        }
        local_4 = 0;
        uVar7 = *(int *)(in_BX + 0x2e) - iVar13;
        if ((int)uVar7 < (int)uVar11) {
          local_4 = uVar11 - uVar7;
          uVar11 = uVar7;
        }
        pbVar12 = in_BX + iVar13 + 0x34;
        for (; uVar11 != 0; uVar11 = uVar11 - 1) {
          pbVar4 = pbVar18;
          pbVar18 = pbVar18 + 1;
          pbVar2 = pbVar12;
          pbVar12 = pbVar12 + 1;
          *pbVar4 = *pbVar2;
        }
        if (local_4 == 0) break;
        iVar13 = 0;
        uVar11 = local_4;
      }
      uVar11 = *(uint *)(in_BX + 0x26);
      iVar13 = *(int *)(in_BX + 0x28);
      uVar7 = param_3[1];
      *(uint *)(in_BX + 0x26) = uVar11 + uVar7;
      *(uint *)(in_BX + 0x28) = iVar13 + (uint)CARRY2(uVar11,uVar7);
      if ((param_2 & 0x100) != 0) {
        return 0;
      }
      bVar20 = 0;
      if ((*(int *)(in_BX + 0x2a) != *(int *)(in_BX + 0x26)) ||
         (*(int *)(in_BX + 0x2c) != *(int *)(in_BX + 0x28))) {
        FUN_1000_77f8();
        iVar13 = FUN_1000_789e();
        if (iVar13 != 0) {
          return 0xffff;
        }
        bVar20 = in_BX[extraout_DX_00 + 0x34];
      }
      pcVar16 = (char *)param_3[2];
      uVar11 = param_3[1];
      iVar13 = 0;
      pcVar14 = pcVar16;
      do {
        if (uVar11 == 0) {
LAB_1000_7b73:
          param_3[1] = param_3[1] - iVar13;
          return 0;
        }
        pcVar15 = pcVar14 + 1;
        cVar6 = *pcVar14;
        uVar7 = uVar11 - 1;
        if (cVar6 == '\x1a') {
          param_3[1] = (int)pcVar16 - param_3[2];
          return 0;
        }
        uVar10 = uVar7;
        iVar8 = iVar13;
        if (cVar6 == '\r') {
          if (uVar7 == 0) {
            cVar6 = '\r';
            if (bVar20 == 10) {
              puVar1 = (uint *)(in_BX + 0x26);
              uVar11 = *puVar1;
              *puVar1 = *puVar1 + 1;
              *(uint *)(in_BX + 0x28) = *(int *)(in_BX + 0x28) + (uint)(0xfffe < uVar11);
              cVar6 = '\n';
            }
            *pcVar16 = cVar6;
            goto LAB_1000_7b73;
          }
          pcVar3 = pcVar15;
          pcVar15 = pcVar14 + 2;
          cVar6 = *pcVar3;
          uVar10 = uVar11 - 2;
          iVar8 = iVar13 + 1;
          if (cVar6 != '\n') {
            pcVar15 = pcVar14 + 1;
            cVar6 = '\r';
            uVar10 = uVar7;
            iVar8 = iVar13;
          }
        }
        pcVar3 = pcVar16;
        pcVar16 = pcVar16 + 1;
        *pcVar3 = cVar6;
        uVar11 = uVar10;
        iVar13 = iVar8;
        pcVar14 = pcVar15;
      } while( true );
    }
    uVar11 = *param_3;
    if ((int)uVar11 < 0) {
      return 1;
    }
    pcVar16 = (char *)param_3[2];
    if ((param_2 & 0x100) == 0) {
      if (uVar11 != 0) {
        if (in_BX[1] == 0) {
          return 1;
        }
        do {
          pcVar5 = (code *)swi(0x21);
          cVar6 = (*pcVar5)();
          if (cVar6 == '\r') {
            *pcVar16 = '\n';
            if (in_BX[2] != 0) {
              pcVar5 = (code *)swi(0x21);
              (*pcVar5)();
            }
            param_3[1] = (uint)(pcVar16 + (1 - param_3[2]));
            return 0;
          }
          if (cVar6 == '\x1a') {
            return 1;
          }
          pcVar3 = pcVar16;
          pcVar16 = pcVar16 + 1;
          *pcVar3 = cVar6;
          uVar11 = uVar11 - 1;
        } while (uVar11 != 0);
      }
    }
    else {
      if (in_BX[3] == 0) {
        return 1;
      }
      for (; uVar11 != 0; uVar11 = uVar11 - 1) {
        pcVar5 = (code *)swi(0x21);
        cVar6 = (*pcVar5)();
        pcVar3 = pcVar16;
        pcVar16 = pcVar16 + 1;
        *pcVar3 = cVar6;
      }
    }
    param_3[1] = *param_3;
  }
  else if (uVar11 == 2) {
    if ((in_AL & 0x80) == 0) {
      uVar11 = *param_3;
      if ((int)uVar11 < 0) {
        return 0xffff;
      }
      if (uVar11 != 0) {
        bVar20 = 0;
        iVar8 = 0;
        uVar19 = FUN_1000_77f8();
        pbVar12 = (byte *)((ulong)uVar19 >> 0x10);
        iVar13 = (int)uVar19;
        uVar19 = FUN_1000_77f8(iVar8,bVar20,iVar13);
        pbVar18 = (byte *)param_3[2];
        while( true ) {
          iVar9 = FUN_1000_789e(iVar8,bVar20,iVar13,uVar19);
          if (iVar9 != 0) {
            return 0xffff;
          }
          in_BX[0x25] = 1;
          local_4 = 0;
          uVar7 = *(int *)(in_BX + 0x2e) - (int)pbVar12;
          if ((int)uVar7 < (int)uVar11) {
            local_4 = uVar11 - uVar7;
            uVar11 = uVar7;
          }
          pbVar12 = in_BX + (int)(pbVar12 + 0x34);
          pbVar17 = pbVar18;
          bVar21 = bVar20;
          if ((param_2 & 0x100) != 0) break;
          do {
            bVar20 = *pbVar17;
            pbVar18 = pbVar17 + 1;
            if ((bVar20 == 10) && (bVar21 != 0xd)) {
              bVar20 = 0xd;
              iVar8 = iVar8 + 1;
              local_4 = local_4 + 1;
              pbVar18 = pbVar17;
            }
            pbVar2 = pbVar12;
            pbVar12 = pbVar12 + 1;
            *pbVar2 = bVar20;
            uVar11 = uVar11 - 1;
            pbVar17 = pbVar18;
            bVar21 = bVar20;
          } while (uVar11 != 0);
          if (local_4 == 0) {
LAB_1000_7c7e:
            uVar11 = *(uint *)(in_BX + 0x26);
            iVar13 = *(int *)(in_BX + 0x28);
            uVar7 = *param_3 + iVar8;
            param_3[1] = uVar7;
            uVar10 = uVar11 + uVar7;
            uVar11 = iVar13 + (uint)CARRY2(uVar11,uVar7);
            *(uint *)(in_BX + 0x26) = uVar10;
            *(uint *)(in_BX + 0x28) = uVar11;
            if (uVar11 < *(uint *)(in_BX + 0x2c)) {
              return 0;
            }
            if ((uVar11 == *(uint *)(in_BX + 0x2c)) && (uVar10 <= *(uint *)(in_BX + 0x2a))) {
              return 0;
            }
            *(uint *)(in_BX + 0x2a) = uVar10;
            *(uint *)(in_BX + 0x2c) = uVar11;
            FUN_1000_77f8();
            iVar13 = extraout_DX_01;
            if (extraout_DX_01 == 0) {
              iVar13 = *(int *)(in_BX + 0x2e);
            }
            *(int *)(in_BX + 0x30) = iVar13;
            return 0;
          }
          pbVar12 = pbVar12 + (-0x34 - (int)in_BX);
          uVar11 = local_4;
          if (pbVar12 == *(byte **)(in_BX + 0x2e)) {
LAB_1000_7c3e:
            pbVar12 = (byte *)0x0;
            iVar13 = iVar13 + 1;
            uVar11 = local_4;
            if ((uint)uVar19 <= *(uint *)(in_BX + 0x32)) {
              *(undefined2 *)(in_BX + 0x30) = *(undefined2 *)(in_BX + 0x2e);
            }
          }
        }
        for (; uVar11 != 0; uVar11 = uVar11 - 1) {
          pbVar4 = pbVar12;
          pbVar12 = pbVar12 + 1;
          pbVar2 = pbVar18;
          pbVar18 = pbVar18 + 1;
          *pbVar4 = *pbVar2;
        }
        if (local_4 == 0) goto LAB_1000_7c7e;
        goto LAB_1000_7c3e;
      }
    }
    else {
      uVar11 = *param_3;
      pcVar16 = (char *)param_3[2];
      unaff_DI = param_3;
      if ((param_2 & 0x100) == 0) {
        if ((uVar11 != 0) && (in_BX[2] != 0)) {
          do {
            pcVar3 = pcVar16;
            pcVar16 = pcVar16 + 1;
            if (*pcVar3 == '\n') {
              pcVar5 = (code *)swi(0x21);
              (*pcVar5)();
            }
            pcVar5 = (code *)swi(0x21);
            (*pcVar5)();
            uVar11 = uVar11 - 1;
          } while (uVar11 != 0);
        }
      }
      else if (in_BX[4] != 0) {
        for (; uVar11 != 0; uVar11 = uVar11 - 1) {
          pcVar5 = (code *)swi(0x21);
          (*pcVar5)();
        }
      }
    }
    unaff_DI[1] = *unaff_DI;
  }
  else if (uVar11 == 4) {
    if ((in_AL & 0x80) == 0) {
      (in_BX + 0x28)[0] = 0;
      (in_BX + 0x28)[1] = 0;
      (in_BX + 0x26)[0] = 0;
      (in_BX + 0x26)[1] = 0;
      in_BX[0x25] = 0;
      (in_BX + 0x32)[0] = 0xff;
      (in_BX + 0x32)[1] = 0xff;
      *(undefined2 *)(in_BX + 0x2a) = *(undefined2 *)(in_BX + 0x10);
      *(undefined2 *)(in_BX + 0x2c) = *(undefined2 *)(in_BX + 0x12);
    }
  }
  else if (uVar11 == 5) {
    if ((in_AL & 0x80) == 0) {
      iVar13 = 0;
      if ((in_BX[0x25] != 0) && (iVar8 = FUN_1000_7854(), iVar8 != 0)) {
        iVar13 = iVar13 + 1;
      }
      pcVar5 = (code *)swi(0x21);
      cVar6 = (*pcVar5)();
      if (cVar6 != '\0') {
        return 0xffff;
      }
      if (iVar13 != 0) {
        return 0xffff;
      }
    }
  }
  else if (uVar11 == 8) {
    if ((in_AL & 0x80) != 0) {
      return 0xffff;
    }
    if ((param_2 & 0x100) == 0) {
      param_3[1] = *(uint *)(in_BX + 0x28);
      *param_3 = *(uint *)(in_BX + 0x26);
    }
    else {
      param_3[1] = *(uint *)(in_BX + 0x2c);
      *param_3 = *(uint *)(in_BX + 0x2a);
    }
  }
  else if (uVar11 == 0xd) {
    *(uint *)(param_1 * 2 + 0x2464) = *param_3;
  }
  else {
    if (uVar11 != 0xe) {
      return 0xffff;
    }
    FUN_1000_88c4(in_BX);
  }
  return 0;
}



// ==== FUN_1000_7d68 @ 1000:7d68 ====

int __cdecl16near FUN_1000_7d68(int param_1,int *param_2)

{
  byte bVar1;
  undefined1 *puVar2;
  int iVar3;
  uint uVar4;
  undefined2 unaff_DS;
  int local_6;
  int local_4;
  
  bVar1 = *(byte *)(param_2 + 3);
  uVar4 = (uint)bVar1;
  if (((bVar1 & 2) == 0) || ((bVar1 & 0x30) != 0)) {
    return -1;
  }
  local_6 = *param_2 - param_2[2];
  local_4 = local_6;
  if (((*(byte *)(param_2 + 3) & 4) != 0) && ((local_6 != 0x200 && (param_1 != -1)))) {
    puVar2 = (undefined1 *)*param_2;
    *param_2 = *param_2 + 1;
    *puVar2 = (char)param_1;
    if (param_1 == 10) {
      local_6 = local_6 + 1;
      local_4 = FUN_1000_6ddd(*(undefined1 *)((int)param_2 + 7),param_2[2],local_6,uVar4);
      *param_2 = param_2[2];
    }
    param_2[1] = 0;
    if (local_4 == local_6) {
      return param_1;
    }
    local_6 = 0;
  }
  if (local_6 != 0) {
    local_4 = FUN_1000_6ddd(*(undefined1 *)((int)param_2 + 7),param_2[2],local_6,uVar4);
    *param_2 = param_2[2];
    if ((*(byte *)(param_2 + 3) & 4) == 0) {
      param_2[1] = 0x200;
    }
    else {
      param_2[1] = 0;
    }
  }
  if (local_4 == -1) {
    *(byte *)(param_2 + 3) = *(byte *)(param_2 + 3) | 0x20;
  }
  else if (local_4 < local_6) {
    *(byte *)(param_2 + 3) = *(byte *)(param_2 + 3) | 0x10;
  }
  if (param_1 == -1) {
    param_1 = 0;
  }
  else {
    iVar3 = param_2[1];
    param_2[1] = iVar3 + -1;
    if (iVar3 + -1 < 0) {
      FUN_1000_7d68(param_1,param_2);
    }
    else {
      puVar2 = (undefined1 *)*param_2;
      *param_2 = *param_2 + 1;
      *puVar2 = (char)param_1;
    }
  }
  if ((*(byte *)(param_2 + 3) & 0x30) != 0) {
    return -1;
  }
  return param_1;
}



// ==== FUN_1000_7eba @ 1000:7eba ====

undefined2 __cdecl16near FUN_1000_7eba(byte *param_1)

{
  byte bVar1;
  undefined2 uVar2;
  int iVar3;
  undefined2 unaff_DS;
  
  if (*param_1 == 0x2d) {
    param_1 = param_1 + 1;
  }
  bVar1 = *(byte *)(*param_1 + 0x2363);
  while ((bVar1 & 4) != 0) {
    param_1 = param_1 + 1;
    bVar1 = *(byte *)(*param_1 + 0x2363);
  }
  if (*param_1 == 0x2e) {
    do {
      param_1 = param_1 + 1;
    } while ((*(byte *)(*param_1 + 0x2363) & 4) != 0);
  }
  if (*param_1 == 0x6c) {
    param_1 = param_1 + 1;
  }
  iVar3 = 0x20;
  do {
    if ((uint)*param_1 == *(uint *)(iVar3 + -0x7dc3)) {
                    /* WARNING: Could not recover jumptable at 0x0001826b. Too many branches */
                    /* WARNING: Treating indirect jump as call */
      uVar2 = (*(code *)*(undefined2 *)(iVar3 + -0x7dc1))();
      return uVar2;
    }
    iVar3 = iVar3 + -4;
  } while (-1 < iVar3);
  return 0;
}



// ==== FUN_1000_86b3 @ 1000:86b3 ====

uint __cdecl16near FUN_1000_86b3(byte *param_1,int *param_2)

{
  byte bVar1;
  int iVar2;
  byte *pbVar3;
  undefined2 unaff_DS;
  uint local_4;
  
  local_4 = 0;
  while( true ) {
    bVar1 = *param_1;
    if (bVar1 == 0) break;
    iVar2 = param_2[1];
    param_2[1] = iVar2 + -1;
    if (iVar2 + -1 < 0) {
      local_4 = FUN_1000_7d68(bVar1,param_2);
      param_1 = param_1 + 1;
    }
    else {
      pbVar3 = (byte *)*param_2;
      *param_2 = *param_2 + 1;
      *pbVar3 = bVar1;
      local_4 = (uint)bVar1;
      param_1 = param_1 + 1;
    }
  }
  return local_4;
}



// ==== FUN_1000_86ff @ 1000:86ff ====

byte * __cdecl16near FUN_1000_86ff(byte *param_1)

{
  byte *pbVar1;
  long lVar2;
  byte bVar3;
  uint in_DX;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  undefined4 uVar4;
  byte *pbVar5;
  int local_18;
  int local_16;
  uint local_14;
  byte local_10 [12];
  byte *local_4;
  
  bVar3 = 0;
  if (*param_1 == 0) {
    return (byte *)CONCAT22(in_DX,(byte *)0x2496);
  }
  for (local_18 = 0; local_18 < 0xb; local_18 = local_18 + 1) {
    local_10[local_18] = 0x20;
  }
  local_18 = 0;
  while ((*param_1 != 0 && (local_18 < 0xb))) {
    pbVar1 = param_1 + 1;
    local_14 = (uint)*param_1;
    if ((*(byte *)(local_14 + 0x2363) & 2) != 0) {
      local_14 = local_14 - 0x20;
    }
    param_1 = pbVar1;
    if (local_14 == 0x2e) {
      if ((local_18 == 0) || (8 < local_18)) {
        return (byte *)((ulong)in_DX << 0x10);
      }
      local_18 = 8;
    }
    else if (local_14 == 0x3a) {
      if (*pbVar1 == 0) break;
      if (local_18 != 1) {
        return (byte *)((ulong)in_DX << 0x10);
      }
      if ((local_10[0] < 0x41) || (0x5a < local_10[0])) {
        return (byte *)((ulong)in_DX << 0x10);
      }
      bVar3 = local_10[0] & 0x1f;
      local_18 = 0;
    }
    else {
      local_10[local_18] = (byte)local_14;
      if ((((int)local_14 < 0x20) || (0x60 < (int)(local_14 - 0x20))) ||
         (*(char *)(local_14 + 0x24c0) == '\0')) {
        return (byte *)((ulong)in_DX << 0x10);
      }
      local_14 = 0;
      local_18 = local_18 + 1;
    }
  }
  local_10[local_18] = 0;
  for (local_16 = 0; local_16 < 6; local_16 = local_16 + 1) {
    uVar4 = FUN_1000_8ff1(local_10,*(undefined2 *)(local_16 * 4 + 0x24c8));
    in_DX = (uint)((ulong)uVar4 >> 0x10);
    if ((int)uVar4 == 0) {
      lVar2 = (long)*(int *)(local_16 * 4 + 0x24ca) * 6;
      return (byte *)CONCAT22((int)((ulong)lVar2 >> 0x10),(byte *)((int)lVar2 + 0x2496));
    }
  }
  if (local_14 != 0x3a) {
    local_10[local_18] = 0x20;
    pbVar5 = (byte *)FUN_1000_88ef(*(int *)0x254a + 0x34);
    local_4 = (byte *)pbVar5;
    if (local_4 != (byte *)0x0) {
      *local_4 = bVar3;
      for (local_18 = 0; local_18 < 0xb; local_18 = local_18 + 1) {
        local_4[local_18 + 1] = local_10[local_18];
      }
      *(undefined2 *)(local_4 + 0x2e) = *(undefined2 *)0x254a;
      return pbVar5;
    }
    return (byte *)((ulong)pbVar5 & 0xffff0000);
  }
  return (byte *)((ulong)in_DX << 0x10);
}



// ==== FUN_1000_88c4 @ 1000:88c4 ====

void __cdecl16near FUN_1000_88c4(byte *param_1)

{
  undefined2 unaff_DS;
  
  if ((*param_1 & 0x80) != 0) {
    return;
  }
  FUN_1000_898f(param_1,*(int *)0x254a + 0x34);
  return;
}



// ==== FUN_1000_88ef @ 1000:88ef ====

undefined2 * __cdecl16near FUN_1000_88ef(int param_1)

{
  int iVar1;
  uint uVar2;
  undefined2 *puVar3;
  undefined2 unaff_DS;
  undefined2 *local_a;
  undefined2 *local_8;
  
  if (param_1 == 0) {
    return (undefined2 *)0x0;
  }
  uVar2 = param_1 + 3U >> 2;
  local_a = (undefined2 *)*(undefined2 *)0x2540;
  local_8 = (undefined2 *)0x2540;
  while( true ) {
    if (local_a == (undefined2 *)0x0) {
      puVar3 = (undefined2 *)FUN_1000_8f62(uVar2 << 2);
      if (puVar3 != (undefined2 *)0xffff) {
        return puVar3;
      }
      return (undefined2 *)0x0;
    }
    if (uVar2 <= (uint)local_a[1]) break;
    local_8 = local_a;
    local_a = (undefined2 *)*local_a;
  }
  if (local_a[1] == uVar2) {
    *local_8 = *local_a;
  }
  else {
    iVar1 = local_a[1];
    local_a[1] = iVar1 - uVar2;
    local_a = local_a + (iVar1 - uVar2) * 2;
  }
  *(int *)0x2542 = *(int *)0x2542 - uVar2;
  return local_a;
}



// ==== FUN_1000_898f @ 1000:898f ====

undefined2 __cdecl16near FUN_1000_898f(undefined2 *param_1,int param_2)

{
  undefined2 *puVar1;
  uint uVar2;
  undefined2 unaff_DS;
  undefined2 *local_10;
  undefined2 *local_c;
  
  if (param_2 == 0) {
    return 0xffff;
  }
  uVar2 = param_2 + 3U >> 2;
  puVar1 = param_1 + uVar2 * 2;
  *(int *)0x2542 = *(int *)0x2542 + uVar2;
  local_10 = (undefined2 *)*(undefined2 *)0x2540;
  local_c = (undefined2 *)0x2540;
  while( true ) {
    if (local_10 == (undefined2 *)0x0) {
      *local_c = param_1;
      *param_1 = 0;
      param_1[1] = uVar2;
      return 0;
    }
    if (puVar1 < local_10) {
      *param_1 = local_10;
      param_1[1] = uVar2;
      *local_c = param_1;
      return 0;
    }
    if (local_10 == puVar1) {
      *param_1 = *local_10;
      param_1[1] = uVar2 + local_10[1];
      *local_c = param_1;
      return 0;
    }
    if (param_1 < local_10 + local_10[1] * 2) break;
    if (param_1 == local_10 + local_10[1] * 2) {
      if (((undefined2 *)*local_10 != (undefined2 *)0x0) && ((undefined2 *)*local_10 < puVar1)) {
        *(int *)0x2542 = *(int *)0x2542 - uVar2;
        return 0xffff;
      }
      local_10[1] = local_10[1] + uVar2;
      if (((undefined2 *)*local_10 != (undefined2 *)0x0) && (puVar1 == (undefined2 *)*local_10)) {
        local_10[1] = local_10[1] + puVar1[1];
        *local_10 = *puVar1;
      }
      return 0;
    }
    local_c = local_10;
    local_10 = (undefined2 *)*local_10;
  }
  *(int *)0x2542 = *(int *)0x2542 - uVar2;
  return 0xffff;
}



// ==== FUN_1000_8b5d @ 1000:8b5d ====

void __cdecl16near FUN_1000_8b5d(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  int unaff_BP;
  int iVar5;
  int iVar6;
  undefined2 unaff_SS;
  bool bVar7;
  bool bVar8;
  
  iVar5 = 0x40;
  uVar1 = 0;
  uVar4 = *(uint *)(unaff_BP + 4);
  uVar2 = *(uint *)(unaff_BP + 6);
  uVar3 = *(uint *)(unaff_BP + 8);
  iVar6 = *(int *)(unaff_BP + 10);
  do {
    bVar7 = iVar6 < 0;
    iVar6 = iVar6 * 2;
    bVar8 = (int)uVar3 < 0;
    uVar3 = uVar3 << 1 | (uint)bVar7;
    bVar7 = (int)uVar2 < 0;
    uVar2 = uVar2 << 1 | (uint)bVar8;
    bVar8 = (int)uVar4 < 0;
    uVar4 = uVar4 << 1 | (uint)bVar7;
    uVar1 = uVar1 << 1 | (uint)bVar8;
    if (9 < uVar1) {
      uVar1 = uVar1 - 10;
      iVar6 = iVar6 + 1;
    }
    iVar5 = iVar5 + -1;
  } while (iVar5 != 0);
  *(uint *)(unaff_BP + 4) = uVar4;
  *(uint *)(unaff_BP + 6) = uVar2;
  *(uint *)(unaff_BP + 8) = uVar3;
  *(int *)(unaff_BP + 10) = iVar6;
  return;
}



// ==== FUN_1000_8b91 @ 1000:8b91 ====

void __cdecl16near FUN_1000_8b91(void)

{
  int iVar1;
  int iVar2;
  int unaff_BP;
  undefined2 unaff_SS;
  
  iVar1 = *(int *)(unaff_BP + 10);
  *(int *)(unaff_BP + 10) = iVar1 << 1;
  iVar2 = *(int *)(unaff_BP + 8);
  *(uint *)(unaff_BP + 8) = iVar2 << 1 | (uint)(iVar1 < 0);
  iVar1 = *(int *)(unaff_BP + 6);
  *(uint *)(unaff_BP + 6) = iVar1 << 1 | (uint)(iVar2 < 0);
  *(uint *)(unaff_BP + 4) = *(int *)(unaff_BP + 4) << 1 | (uint)(iVar1 < 0);
  return;
}



// ==== FUN_1000_8bb2 @ 1000:8bb2 ====

int __cdecl16near FUN_1000_8bb2(void)

{
  int in_AX;
  
  return in_AX * 10;
}



// ==== FUN_1000_8bc8 @ 1000:8bc8 ====

void __cdecl16near FUN_1000_8bc8(void)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  int unaff_BP;
  int iVar4;
  undefined2 unaff_SS;
  
  iVar3 = 0;
  iVar4 = 6;
  do {
    *(int *)(unaff_BP + iVar4 + 4) = iVar3;
    uVar2 = FUN_1000_8bb2();
    uVar1 = *(uint *)(unaff_BP + iVar4 + 4);
    iVar3 = iVar3 + (uint)CARRY2(uVar2,uVar1);
    *(int *)(unaff_BP + iVar4 + 4) = uVar2 + uVar1;
    iVar4 = iVar4 + -2;
  } while (-1 < iVar4);
  return;
}



// ==== FUN_1000_8be6 @ 1000:8be6 ====

void __cdecl16near FUN_1000_8be6(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  int unaff_BP;
  int unaff_SI;
  undefined2 unaff_SS;
  
  uVar3 = *(uint *)(unaff_BP + 4);
  uVar6 = *(uint *)(unaff_BP + 6);
  uVar4 = *(uint *)(unaff_BP + 8);
  uVar5 = *(uint *)(unaff_BP + 10);
  do {
    uVar2 = uVar3 & 1;
    uVar3 = uVar3 >> 1;
    uVar1 = uVar6 & 1;
    uVar6 = uVar6 >> 1 | (uint)(uVar2 != 0) << 0xf;
    uVar2 = uVar4 & 1;
    uVar4 = uVar4 >> 1 | (uint)(uVar1 != 0) << 0xf;
    uVar5 = uVar5 >> 1 | (uint)(uVar2 != 0) << 0xf;
    unaff_SI = unaff_SI + -1;
  } while (unaff_SI != 0);
  *(uint *)(unaff_BP + 4) = uVar3;
  *(uint *)(unaff_BP + 6) = uVar6;
  *(uint *)(unaff_BP + 8) = uVar4;
  *(uint *)(unaff_BP + 10) = uVar5;
  return;
}



// ==== FUN_1000_8c0a @ 1000:8c0a ====

/* WARNING: Removing unreachable block (ram,0x00018cb2) */

int __cdecl16near
FUN_1000_8c0a(uint *param_1,int param_2,int param_3,int *param_4,undefined2 *param_5,char *param_6)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  bool bVar4;
  char cVar5;
  uint uVar6;
  undefined2 uVar7;
  int iVar8;
  uint uVar9;
  int iVar10;
  int iVar11;
  undefined2 unaff_SS;
  undefined2 unaff_DS;
  uint local_26;
  uint local_24;
  uint local_22;
  uint local_20;
  int local_1e;
  int local_1c;
  int local_1a;
  char acStack_16 [20];
  
  local_1e = 0;
  uVar1 = param_1[3];
  bVar4 = false;
  uVar6 = uVar1 & 0x7fff;
  if ((((uVar6 == 0) && (param_1[2] == 0)) && (param_1[1] == 0)) && (*param_1 == 0)) {
    iVar11 = 0;
    bVar4 = true;
    goto LAB_1000_8cc1;
  }
  local_1c = (uVar6 >> 4) - 0x3fe;
  local_22 = *param_1;
  local_24 = param_1[1];
  uVar6 = param_1[2];
  uVar9 = param_1[3];
  local_20 = 0;
  iVar11 = 5;
  do {
    uVar3 = uVar9 & 1;
    uVar9 = uVar9 >> 1;
    uVar2 = uVar6 & 1;
    uVar6 = uVar6 >> 1 | (uint)(uVar3 != 0) << 0xf;
    uVar3 = local_24 & 1;
    local_24 = local_24 >> 1 | (uint)(uVar2 != 0) << 0xf;
    uVar2 = local_22 & 1;
    local_22 = local_22 >> 1 | (uint)(uVar3 != 0) << 0xf;
    local_20 = local_20 >> 1 | (uint)(uVar2 != 0) << 0xf;
    iVar11 = iVar11 + -1;
  } while (iVar11 != 0);
  local_26 = uVar6 | 0x8000;
  local_1e = 0;
  while( true ) {
    iVar8 = 0;
    iVar11 = 0;
    if (local_1c == 0) break;
    if (local_1c < 0) {
      if (local_1c + 3 < 0) {
        local_1c = local_1c + 4;
        FUN_1000_8be6();
        FUN_1000_8bc8();
        local_1e = local_1e + -1;
      }
      else {
        FUN_1000_8be6();
        local_1c = local_1c + 1;
      }
    }
    else {
      FUN_1000_8b5d();
      local_1e = local_1e + 1;
    }
  }
  while( true ) {
    acStack_16[iVar11] = (char)iVar8 + '0';
    iVar11 = iVar11 + 1;
    if (0x13 < iVar11) break;
LAB_1000_8cc1:
    iVar8 = 0;
    if ((!bVar4) && ((local_26 != 0 || local_24 != 0 || (local_22 != 0 || local_20 != 0)))) {
      while ((FUN_1000_8bc8(), iVar8 == 0 && (iVar11 == 1))) {
        local_1e = local_1e + -1;
      }
    }
  }
  local_1a = 1;
  iVar11 = param_2;
  if (param_3 != 0) {
    iVar11 = param_2 + local_1e + -1;
    iVar8 = 1;
    if (iVar11 < 0) goto LAB_1000_8d3e;
  }
  iVar8 = 0x14;
  if (iVar11 < 0x12) {
    cVar5 = acStack_16[iVar11 + 1] + '\x05';
    iVar10 = iVar11;
    do {
      iVar8 = iVar11;
      if (cVar5 < ':') goto LAB_1000_8d3e;
      acStack_16[iVar10 + 1] = '0';
      acStack_16[iVar10] = acStack_16[iVar10] + '\x01';
      cVar5 = acStack_16[iVar10];
      iVar10 = iVar10 + -1;
    } while (-1 < iVar10);
    local_1e = local_1e + 1;
    local_1a = 0;
    if (param_3 != 0) {
      iVar8 = iVar11 + 1;
    }
  }
LAB_1000_8d3e:
  iVar11 = 0;
  do {
    *param_6 = acStack_16[local_1a];
    iVar11 = iVar11 + 1;
    param_6 = param_6 + 1;
    if (iVar8 <= iVar11) goto LAB_1000_8d62;
    local_1a = local_1a + 1;
  } while (local_1a < 0x14);
  do {
    *param_6 = '0';
    param_6 = param_6 + 1;
    iVar11 = iVar11 + 1;
  } while (iVar11 < param_2);
LAB_1000_8d62:
  uVar7 = 0;
  if (((int)uVar1 < 0) && (!bVar4)) {
    uVar7 = 0xffff;
  }
  *param_5 = uVar7;
  *param_4 = local_1e;
  if (bVar4) {
    iVar8 = 0;
  }
  return iVar8;
}



// ==== FUN_1000_8f62 @ 1000:8f62 ====

int __cdecl16near FUN_1000_8f62(int param_1)

{
  undefined2 uVar1;
  int iVar2;
  uint uVar3;
  undefined2 unaff_DS;
  
  if (*(int *)0x254c == 0) {
    iVar2 = FUN_1000_9035(*(undefined2 *)0x2494);
    *(int *)0x254c = iVar2;
    if (iVar2 == 0) {
      return -1;
    }
    uVar1 = *(undefined2 *)*(undefined2 *)0x254c;
    *(undefined2 *)0x254e = (undefined2 *)*(undefined2 *)0x254c;
    *(undefined2 *)0x2552 = uVar1;
    *(undefined2 *)0x2550 = uVar1;
  }
  if (param_1 == 0) {
    return -1;
  }
  uVar3 = param_1 + 1U >> 1;
  if (*(uint *)0x2552 < uVar3) {
    return -1;
  }
  *(int *)0x2552 = *(int *)0x2552 - uVar3;
  iVar2 = *(int *)0x254e;
  *(int *)0x254e = iVar2 + uVar3 * 2;
  return iVar2;
}



// ==== FUN_1000_8fde @ 1000:8fde ====

void __cdecl16near FUN_1000_8fde(void)

{
  undefined2 uVar1;
  undefined2 unaff_DS;
  
  uVar1 = *(undefined2 *)0x2550;
  *(undefined2 *)0x254e = *(undefined2 *)0x254c;
  *(undefined2 *)0x2552 = uVar1;
  return;
}



// ==== FUN_1000_8ff1 @ 1000:8ff1 ====

int __cdecl16near FUN_1000_8ff1(byte *param_1,byte *param_2)

{
  undefined2 unaff_DS;
  
  while( true ) {
    if (*param_1 != *param_2) {
      return (uint)*param_1 - (uint)*param_2;
    }
    if (*param_1 == 0) break;
    param_1 = param_1 + 1;
    param_2 = param_2 + 1;
  }
  return 0;
}



// ==== FUN_1000_9035 @ 1000:9035 ====

uint * __cdecl16near FUN_1000_9035(uint param_1)

{
  uint *puVar1;
  undefined1 *puVar2;
  undefined2 unaff_DS;
  
  puVar2 = (undefined1 *)(*(uint *)0x0 - param_1);
  if (((param_1 <= *(uint *)0x0) && ((undefined1 *)*(uint *)0x2 <= puVar2)) &&
     (puVar2 < &stack0xfffe)) {
    puVar1 = (uint *)*(int *)0x2;
    *(uint *)0x2 = (uint)puVar2;
    *puVar1 = (uint)((int)puVar2 - (int)puVar1) >> 1;
    return puVar1;
  }
  return (uint *)0x0;
}



