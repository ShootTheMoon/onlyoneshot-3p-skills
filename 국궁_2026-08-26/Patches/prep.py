import re
fbx = r"C:\Users\banav\Downloads\Viewmodel_WIP (2)\Export\Gukgung_Viewmodel_Split.fbx"
raw = open(fbx, "rb").read()
want = ["Right_Arm_Mesh","Left_Arm_Mesh","Gukgung_Limb","Gukgung_Grip","Gukgung_String","Gukgung_Tip",
        "GukgungArrow_Shaft","GukgungArrow_Nock","GukgungArrow_Point","GukgungArrow_Stripe","GukgungArrow_Vane"]
print("FBX 안의 오브젝트 이름:")
for w in want:
    print("  %-22s %s" % (w, "OK" if w.encode() in raw else "!! 없음"))

def lin2srgb(c):
    return 12.92*c if c <= 0.0031308 else 1.055*(c**(1/2.4)) - 0.055
mats = {
 "Gukgung_Limb":        (0.5144, 0.4120, 0.3384),
 "Gukgung_Grip":        (0.0951, 0.0684, 0.0414),
 "Gukgung_String":      (0.7683, 0.7043, 0.6492),
 "Gukgung_Tip":         (0.5398, 0.2092, 0.2325),
 "GukgungArrow_Shaft":  (0.020, 0.020, 0.024),
 "GukgungArrow_Nock":   (0.930, 0.920, 0.880),
 "GukgungArrow_Point":  (0.720, 0.530, 0.200),
 "GukgungArrow_Stripe": (0.720, 0.850, 0.200),
 "GukgungArrow_Vane":   (0.100, 0.200, 0.620),
}
print("\nViewmodelConfig COLORS 용 (선형 -> sRGB 0~255):")
for k, v in mats.items():
    r, g, b = [int(round(lin2srgb(c)*255)) for c in v]
    print("\t\t\t%-22s = { %3d, %3d, %3d }," % (k, r, g, b))
