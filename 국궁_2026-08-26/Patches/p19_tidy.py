# -*- coding: utf-8 -*-
"""내가 쓴 군더더기 한 줄 정리 (a.stuck and a.vel or a.vel 은 그냥 a.vel 이다)."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch
ok = patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [("\t\t\t\ta.part.CFrame = alignZCFrame(a.pos, a.stuck and a.vel or a.vel)",
      "\t\t\t\ta.part.CFrame = alignZCFrame(a.pos, a.vel)")],
    "ViewmodelController",
)
sys.exit(0 if ok else 1)
