# -*- coding: utf-8 -*-
"""korea 의 화면 오프셋만 { 30, -35, -55 } 로. japan 은 안 건드린다."""
import sys
sys.path.insert(0, r"C:\Users\banav\AppData\Local\Temp\claude\C--Users-banav\bf762b67-1a0b-4ede-8de8-848987e642e4\scratchpad")
from ovdr import patch

ok = patch(
    'SOURCE = "Gukgung_Viewmodel_Merged"',
    [
        (
'''\t\t\tPIVOT = { -540.620941, 18.364028, -1038.147034 },
\t\t\tOFFSET = { -10, -35, -55 },''',
'''\t\t\tPIVOT = { -540.620941, 18.364028, -1038.147034 },
\t\t\t-- 사용자가 화면 보며 맞춘 값. X 는 오른쪽(+) / 왼쪽(-), 단위 cm.
\t\t\t-- japan 과 완전히 별개다 (japan 은 -10 그대로).
\t\t\tOFFSET = { 30, -35, -55 },'''),
    ],
    "ViewmodelConfig",
)
print("\n성공" if ok else "\n★ 실패")
sys.exit(0 if ok else 1)
