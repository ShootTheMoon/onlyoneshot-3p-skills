# -*- coding: utf-8 -*-
"""레벨 파일에서 국궁 뷰모델 파츠의 실제 Size / CFrame 을 읽는다."""
import io, json, re, sys

PATH = r"C:\Users\banav\Documents\OverdareStudio\over_onlyonetap\onlyoneshot.ovdrjm"
s = io.open(PATH, encoding="utf-16-le", errors="replace").read()
if s and s[0] == "\ufeff":
    s = s[1:]
doc = json.loads(s)

WANT = {"Gukgung_Bow", "Gukgung_String", "Arrow_Gukgung",
        "Right_Arm_Mesh", "Left_Arm_Mesh", "Gukgung_Viewmodel_Merged"}

found = []

def walk(node, path):
    if isinstance(node, dict):
        nm = node.get("Name")
        if isinstance(nm, str) and nm in WANT:
            found.append((path, node))
        for k, v in node.items():
            if k not in ("Source",):
                walk(v, path + "/" + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + "[%d]" % i)

walk(doc, "")

def num(v):
    if isinstance(v, (int, float)):
        return round(float(v), 3)
    return v

for path, n in found:
    cls = n.get("ClassName") or n.get("Class") or "?"
    print("%-26s %-12s  %s" % (n.get("Name"), cls, path[-70:]))
    for key in ("Size", "CFrame", "Position", "Orientation", "Rotation", "MeshId", "Scale"):
        if key in n:
            v = n[key]
            if isinstance(v, dict):
                v = {k: num(x) for k, x in v.items()}
            elif isinstance(v, list):
                v = [num(x) for x in v]
            print("     %-12s %s" % (key, v))
    print()
print("총 %d 개" % len(found))
