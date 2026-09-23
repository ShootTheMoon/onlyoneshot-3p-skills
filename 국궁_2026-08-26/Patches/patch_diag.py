# -*- coding: utf-8 -*-
"""뷰모델을 만들 때 어떤 값으로 만들었는지 한 줄 찍는다. 지역변수는 안 늘린다."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    'local VIEWMODEL_SOURCE_NAME = "Wakizashi_Viewmodel_Split"',
    [
        (
'''\tviewmodel.Name = RUNTIME_VIEWMODEL_NAME
\tviewmodel.Parent = Workspace
\tprepareViewmodelParts(viewmodel)''',
'''\tviewmodel.Name = RUNTIME_VIEWMODEL_NAME
\tviewmodel.Parent = Workspace
\tprepareViewmodelParts(viewmodel)

\t-- 진단용 : 무엇을 어떤 값으로 만들었는지 남긴다.
\t-- 나라별 뷰모델이 서로 값을 물고 가는지 여기서 바로 드러난다.
\tdo
\t\tlocal cnt = 0
\t\tfor _ in pairs(viewmodelPartsByName) do cnt = cnt + 1 end
\t\tlocal p, o = SOURCE_PIVOT.Position, CAMERA_OFFSET.Position
\t\tprint(string.format(
\t\t\t"[VM] pick=%s src=%s parts=%d pivot=(%.1f, %.1f, %.1f) offset=(%.0f, %.0f, %.0f)",
\t\t\ttostring(_G.MyPick), tostring(VIEWMODEL_SOURCE_NAME), cnt,
\t\t\tp.X, p.Y, p.Z, o.X, o.Y, o.Z))
\tend'''),
    ],
    "ViewmodelController",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)
