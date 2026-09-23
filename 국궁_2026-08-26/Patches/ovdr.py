# -*- coding: utf-8 -*-
"""onlyoneshot.ovdrjm 안의 스크립트 Source 를 안전하게 갈아끼운다.

전체 JSON 을 재직렬화하지 않는다 (14MB 안의 float 정밀도가 바뀌면 레벨 전체가 흔들린다).
"Source": "..." 문자열만 찾아서 그 구간만 바꿔치기한다.
"""
import io, json, sys

PATH = r"C:\Users\banav\Documents\OverdareStudio\over_onlyonetap\onlyoneshot.ovdrjm"
KEY = '"Source":'


def load():
    with io.open(PATH, "r", encoding="utf-16") as f:
        return f.read()


def save(txt):
    with io.open(PATH, "w", encoding="utf-16") as f:
        f.write(txt)


def find_sources(txt):
    """[(start_of_string_literal, end_exclusive, decoded_text)] 목록."""
    out = []
    i = 0
    while True:
        i = txt.find(KEY, i)
        if i < 0:
            break
        j = i + len(KEY)
        while j < len(txt) and txt[j] in " \t\r\n":
            j += 1
        if j >= len(txt) or txt[j] != '"':
            i = j
            continue
        k = j + 1
        while k < len(txt):
            c = txt[k]
            if c == "\\":
                k += 2
                continue
            if c == '"':
                break
            k += 1
        lit = txt[j:k + 1]
        try:
            out.append((j, k + 1, json.loads(lit)))
        except Exception:
            pass
        i = k + 1
    return out


def patch(signature, edits, label):
    """signature 를 포함하는 Source 하나를 찾아 edits[(old,new)] 를 순서대로 적용."""
    txt = load()
    hits = [s for s in find_sources(txt) if signature in s[2]]
    if len(hits) != 1:
        print("[%s] 실패: signature 매칭 %d건 (1건이어야 함)" % (label, len(hits)))
        return False
    start, end, src = hits[0]
    new = src
    for old, rep in edits:
        o = old.replace("\n", "\r\n") if "\r\n" in new else old
        r = rep.replace("\n", "\r\n") if "\r\n" in new else rep
        n = new.count(o)
        if n != 1:
            print("[%s] 실패: 앵커 %d건 -> %r" % (label, n, old[:60]))
            return False
        new = new.replace(o, r)
    if new == src:
        print("[%s] 변화 없음" % label)
        return False
    txt = txt[:start] + json.dumps(new, ensure_ascii=False) + txt[end:]
    save(txt)
    print("[%s] OK  (%d -> %d chars)" % (label, len(src), len(new)))
    return True


if __name__ == "__main__":
    txt = load()
    for s in find_sources(txt):
        head = s[2].splitlines()[0][:70] if s[2].strip() else "(빈 스크립트)"
        print("%8d  %s" % (len(s[2]), head))
