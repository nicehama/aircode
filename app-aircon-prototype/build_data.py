# -*- coding: utf-8 -*-
"""work-aircon-codes/content.py 의 BLOCKS 를 앱용 구조화 JSON 으로 변환한다.

표(table)를 절 제목 맥락으로 분류해 검색용 코드 항목, LED 판독용 데이터,
체크리스트, 제조사 문의처로 나눈다. content.py 가 갱신되어 표 순서가 바뀌어도
제목(h1/h2) 기준으로 찾도록 작성했다.
"""
import json
import re
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "work-aircon-codes"))
import importlib
import content
importlib.reload(content)

BRAND_ORDER = ["samsung", "lg", "carrier", "winia", "paseco", "fcu"]
BRANDS = {
    "samsung": {"name": "삼성전자", "short": "삼성", "color": "#1428A0"},
    "lg": {"name": "LG전자", "short": "LG", "color": "#A50034"},
    "carrier": {"name": "캐리어", "short": "캐리어", "color": "#0072BC"},
    "winia": {"name": "위니아", "short": "위니아", "color": "#E60012"},
    "paseco": {"name": "파세코", "short": "파세코", "color": "#F58220"},
    "fcu": {"name": "FCU", "short": "FCU", "color": "#00857C"},
}

RESET = {
    "samsung": "실내기 플러그를 뽑거나 분전반의 에어컨 전용 차단기를 내리고 약 1분 뒤 재투입합니다. 리모컨 OFF는 리셋이 아닙니다.",
    "lg": "실내기 차단기를 내렸다가 3분 뒤 실외기 차단기와 함께 투입합니다(3~5분). 설치 직후라면 고객센터 접수보다 설치 서비스매니저 확인이 먼저입니다.",
    "carrier": "전원을 완전히 끊고 10분 뒤 재투입합니다. ER(숫자 없음) 코드는 20~30분 뒤 재연결합니다.",
    "winia": "전원 코드를 빼고 약 5분 뒤 재연결합니다. CL·SE·AU는 고장이 아닌 청소·절전·자동운전 표시입니다.",
    "paseco": "전원을 끄고 1~2분(모델에 따라 3분) 뒤 다시 켭니다. 창문형은 후면 배기구가 막히지 않았는지 함께 봅니다.",
    "fcu": "팬코일 전용 차단기를 내렸다 올린 뒤, 냉온수 공급과 밸브 개방 상태를 함께 확인합니다. 표시등이 정상인데 바람이 안 시원하면 설비(냉온수)를 먼저 봅니다.",
}


def norm(s):
    return re.sub(r"\s+", "", str(s or "")).upper()


def parse_code_tokens(display, brand):
    """표시 문자열에서 검색용 코드 토큰 목록을 만든다."""
    s = str(display or "").replace("\n", " / ")
    s = s.replace("·", "/").replace("，", ",")
    parts = re.split(r"\s*[/,]\s*", s)
    out = []

    def add(tok):
        tok = tok.strip()
        if not tok:
            return
        tok = re.sub(r"\s+", " ", tok)
        if tok not in out:
            out.append(tok)

    for p in parts:
        p = p.strip()
        if not p:
            continue
        m = re.match(r"^(.*?)\((.*?)\)$", p)
        if m:
            add(m.group(1))
            add(m.group(2))
            continue
        m = re.match(r"^(\D*?)(\d+)\s*[~\-]\s*(\D*?)(\d+)$", p)
        if m and len(m.group(2)) <= 3:
            head1, n1, head2, n2 = m.group(1), int(m.group(2)), m.group(3), int(m.group(4))
            head = head2 if head2 else head1
            if 0 <= n2 - n1 <= 40:
                for n in range(n1, n2 + 1):
                    add("%s%d" % (head, n))
                add(p)
                continue
        add(p)

    # 삼성 3자리 C/E 상호 별칭
    if brand == "samsung":
        extra = []
        for t in out:
            tn = norm(t)
            if re.match(r"^[CE]\d{3}$", tn):
                extra.append(("E" if tn[0] == "C" else "C") + tn[1:])
        for e in extra:
            add(e)
    return out


def numeric_alias(tokens):
    nums = []
    for t in tokens:
        tn = norm(t)
        m = re.match(r"^(?:CH|ER|E|C|F|P|X)(\d{1,3})$", tn)
        if m:
            nums.append(m.group(1))
        elif re.match(r"^\d{1,3}$", tn):
            nums.append(tn.lstrip("0") or "0")
    return sorted(set(nums))


CAT_RULES = [
    ("상태 표시", ["고장이 아닙", "고장 아님", "정상", "알림", "절전", "자동운전", "표시 범위", "예약 기능"]),
    ("배수", ["배수", "드레인", "만수", "워터펌프", "워터 모터", "플로트", "수위", "물받이"]),
    ("냉매·압력", ["냉매", "가스 부족", "가스가 원활", "압력", "과열도", "누설", "저압", "고압"]),
    ("센서", ["센서", "써미스터"]),
    ("인버터·압축기", ["압축기", "IPM", "인버터", "PFC", "기동", "권선", "모터 위치", "전동변"]),
    ("팬·송풍", ["팬", "송풍"]),
    ("통신", ["통신", "신호를 주고받", "주소", "모뎀", "릴레이"]),
    ("설치·설정", ["설정값", "설정", "시운전", "설치", "대수", "배관 연결", "오결선", "운전모드", "옵션"]),
    ("전원", ["전원", "정전", "과전압", "저전압", "결상", "역상", "차단기", "퓨즈"]),
]


def category_of(cause, section):
    text = re.split(r"\(", cause or "")[0] + " " + (section or "")
    for name, kws in CAT_RULES:
        for kw in kws:
            if kw in text:
                return name
    return "기타"


def split_steps(check):
    if not check:
        return []
    return [p.strip() for p in re.split(r"\s*(?:→|->)\s*", check) if p.strip()]


# ------------------------------------------------------------------ 수집
entries = []
led = {
    "lgPcb": [],          # {code, red, green, cause, note}
    "cassette": [],       # {form, tokens[], cause, check, group}
    "carrierLamp": [],    # {display, product, cause, check}
    "order": [],          # 불을 읽는 순서
    "readGuide": [],      # LG 표시 위치별 읽는 법
    "formMeta": [],       # 제품 형태별 램프 개수/아이콘
    "record": [],         # 현장 기록 항목
    "summary": [],        # 6-8 요약
}
brand_notes = {}
centers_b = []
centers_fcu = []
checklist = []
safety = []
intro_tables = []
unknown_tables = []

h1 = ""
h2 = ""
pending_note_key = None

for idx, b in enumerate(content.BLOCKS):
    t = b["t"]
    if t == "h1":
        h1 = b["text"]
        h2 = ""
        continue
    if t == "h2":
        h2 = b["text"]
        continue
    if t != "table":
        continue

    cols = b["cols"]
    rows = b["rows"]
    ctx = h1 + " || " + h2

    # ---------------- 부록 A 체크리스트
    if h1.startswith("부록 A"):
        for r in rows:
            name = r[0].replace("\n", " ")
            core = re.sub(r"\s*\(.*?\)\s*", "", name).strip()
            checklist.append({
                "id": "ck%d" % (len(checklist) + 1),
                "name": core,
                "full": name,
                "codes": r[1].replace("\n", " "),
                "steps": split_steps(r[2].replace("\n", " ")),
                "criteria": r[3].replace("\n", " "),
            })
        continue

    # ---------------- 부록 B 제조사 고객센터
    if h1.startswith("부록 B"):
        for r in rows:
            centers_b.append({
                "maker": r[0].replace("\n", " "),
                "phone": r[1].replace("\n", " "),
                "info": r[2].replace("\n", " "),
            })
        continue

    # ---------------- 7-6 FCU 문의처
    if h2.startswith("7-6"):
        for r in rows:
            raw_phone = re.sub(r"\s*·.*$", "", r[3].replace("\n", " "))
            centers_fcu.append({
                "maker": r[0].replace("\n", " ") + (" (FCU)" if "FCU" not in r[0] else ""),
                "phone": raw_phone if re.search(r"\d", raw_phone) else "",
                "info": (r[1].replace("\n", " ") + " · " + r[3].replace("\n", " ")).strip(" ·"),
            })
        continue

    # ---------------- 7장 FCU 코드
    if h1.startswith("7."):
        vendor = "FCU"
        if h2.startswith("7-1"):
            vendor = "신우공조"
        elif h2.startswith("7-2"):
            vendor = "삼성전자 FCU"
        elif h2.startswith("7-3"):
            vendor = "에이피(주)"
        for r in rows:
            display = r[0].replace("\n", " ")
            cause = r[1].replace("\n", " ")
            check = r[2].replace("\n", " ")
            extra = {}
            if len(r) > 3:
                extra["ledColor"] = r[3].replace("\n", " ")
                check = check + (" · LED " + extra["ledColor"] if extra["ledColor"] else "")
            tokens = parse_code_tokens(display, "fcu")
            entries.append({
                "id": "fcu-%d" % len(entries),
                "brand": "fcu",
                "brandName": vendor,
                "chips": ["fcu"] + (["samsung"] if vendor.startswith("삼성") else []),
                "device": ["FCU"],
                "section": h1.split(".")[1].strip() if "." in h1 else h1,
                "sectionTitle": h2.replace("7-", "7-"),
                "display": display,
                "codes": tokens,
                "nums": numeric_alias(tokens),
                "cause": cause,
                "check": check,
                "steps": split_steps(check),
                "category": category_of(cause, h2),
                "reset": RESET["fcu"],
                "kind": "code",
            })
        continue

    # ---------------- 파세코
    if h1.startswith("5."):
        for r in rows:
            display = r[0].replace("\n", " ")
            cause = r[1].replace("\n", " ")
            check = r[2].replace("\n", " ")
            tokens = parse_code_tokens(display, "paseco")
            entries.append({
                "id": "paseco-%d" % len(entries),
                "brand": "paseco",
                "brandName": "파세코",
                "chips": ["paseco"],
                "device": ["창문형"],
                "section": "5. 참고 부록",
                "sectionTitle": "창문형 에어컨",
                "display": display,
                "codes": tokens,
                "nums": numeric_alias(tokens),
                "cause": cause,
                "check": check,
                "steps": split_steps(check),
                "category": category_of(cause, h2),
                "reset": RESET["paseco"],
                "kind": "code",
            })
        continue

    # ---------------- 6장 LED 자료
    if h1.startswith("6."):
        first = cols[0]
        if first == "순서":
            for r in rows:
                led["order"].append([c.replace("\n", " ") for c in r])
        elif first == "제품 형태":
            for r in rows:
                led["formMeta"].append({
                    "form": r[0].replace("\n", " "),
                    "lamps": r[1].replace("\n", " "),
                    "icons": r[2].replace("\n", " "),
                })
        elif first == "표시 위치":
            for r in rows:
                led["readGuide"].append([c.replace("\n", " ") for c in r])
        elif first == "기록 항목":
            for r in rows:
                led["record"].append([c.replace("\n", " ") for c in r])
        elif first == "제조사":
            for r in rows:
                led["summary"].append([c.replace("\n", " ") for c in r])
        elif "적색 LED 점멸" in cols:
            for r in rows:
                red = re.sub(r"[^0-9]", "", r[1])
                green = re.sub(r"[^0-9]", "", r[2])
                cause = r[3].replace("\n", " ")
                led["lgPcb"].append({
                    "code": r[0].replace("\n", " ").strip(),
                    "red": int(red) if red else 0,
                    "green": int(green) if green else 0,
                    "cause": cause,
                    "check": "",
                })
        elif first in ("깜박이는 램프", "램프 표시"):
            form = "360 원형"
            group = "360"
            if h2.startswith("②"):
                form, group = "4WAY · 램프 4개", "4WAY4"
            elif h2.startswith("③"):
                form, group = "4WAY · 램프 5개", "4WAY5"
            elif h2.startswith("④"):
                form, group = "1WAY · 램프 4개", "1WAY4"
            for r in rows:
                disp = r[0].replace("\n", " ")
                cause = r[1].replace("\n", " ")
                check = r[2].replace("\n", " ")
                tokens = []
                for part in re.split(r"\s*\+\s*", disp):
                    part = part.strip()
                    for name in ["전원", "물방울", "바람개비", "시계", "바둑판"]:
                        if name in part:
                            tokens.append(name)
                    if "전체" in part:
                        tokens.append("전체")
                    if "하늘" in part and "간격" not in part:
                        tokens.append("하늘색")
                    if "연두" in part and "간격" not in part:
                        tokens.append("연두색")
                    if "파란" in part and "간격" not in part:
                        tokens.append("파란색")
                    if "빨간" in part and "간격" not in part:
                        tokens.append("빨간색")
                led["cassette"].append({
                    "form": form,
                    "group": group,
                    "display": disp,
                    "tokens": tokens,
                    "cause": cause,
                    "check": check,
                })
                entries.append({
                    "id": "led-%d" % len(entries),
                    "brand": "samsung",
                    "brandName": "삼성전자",
                    "chips": ["samsung"],
                    "device": ["카세트"],
                    "section": "6-2. 삼성 카세트 램프",
                    "sectionTitle": form,
                    "display": disp,
                    "codes": [],
                    "nums": [],
                    "cause": cause,
                    "check": check,
                    "steps": split_steps(check),
                    "category": category_of(cause, h2),
                    "reset": RESET["samsung"],
                    "kind": "led",
                    "ledForm": group,
                    "ledTokens": tokens,
                })
        elif first == "표시":
            for r in rows:
                led["carrierLamp"].append({
                    "display": re.sub(r"\s*\n\s*", " · ", r[0]).strip(),
                    "product": r[1].replace("\n", " "),
                    "cause": r[2].replace("\n", " "),
                    "check": r[3].replace("\n", " "),
                })
                entries.append({
                    "id": "led-%d" % len(entries),
                    "brand": "carrier",
                    "brandName": "캐리어",
                    "chips": ["carrier"],
                    "device": ["벽걸이"] if "벽걸이" in r[1] else ["스탠드", "시스템"],
                    "section": "6-5. 캐리어 램프",
                    "sectionTitle": "표시창이 없는 기종",
                    "display": re.sub(r"\s*\n\s*", " · ", r[0]).strip(),
                    "codes": [],
                    "nums": [],
                    "cause": r[2].replace("\n", " "),
                    "check": r[3].replace("\n", " "),
                    "steps": split_steps(r[3]),
                    "category": category_of(r[2], h2),
                    "reset": RESET["carrier"],
                    "kind": "led",
                })
        else:
            unknown_tables.append((idx, h1, h2, cols))
        continue

    # ---------------- 1~4장 코드 표
    if not (first := cols[0]) in ("코드", "표시"):
        unknown_tables.append((idx, h1, h2, cols))
        continue
    if h2 and (h2.endswith("점검 포인트") or h2.startswith("이 자료") or h2.startswith("제조사별") or h2.startswith("모든")):
        intro_tables.append((idx, h1, h2, cols))

    brand = None
    devices = []
    if h1.startswith("1."):
        brand = "samsung"
        if h2.startswith("1-6"):
            devices = ["스탠드", "벽걸이"]
        else:
            devices = ["시스템"]
    elif h1.startswith("2."):
        brand = "lg"
        devices = ["시스템"] if h2.startswith(("2-1", "2-2", "2-3")) else ["스탠드", "벽걸이"]
    elif h1.startswith("3."):
        brand = "carrier"
        if h2.startswith("3-5"):
            devices = ["시스템"]
        elif h2.startswith("3-1") or h2.startswith("3-2") or h2.startswith("3-3"):
            devices = ["스탠드", "벽걸이", "창문형"]
        else:
            devices = ["스탠드", "벽걸이"]
    elif h1.startswith("4."):
        brand = "winia"
        devices = ["스탠드"] if h2.startswith("4-1") else ["벽걸이", "멀티"]

    if brand is None:
        unknown_tables.append((idx, h1, h2, cols))
        continue

    for r in rows:
        display = re.sub(r"\s*\n\s*", " · ", r[0]).strip()
        cause = r[1].replace("\n", " ")
        check = r[2].replace("\n", " ") if len(r) > 2 else ""
        tokens = parse_code_tokens(r[0], brand) if first == "코드" else []
        entries.append({
            "id": "%s-%d" % (brand, len(entries)),
            "brand": brand,
            "brandName": BRANDS[brand]["name"],
            "chips": [brand],
            "device": devices,
            "section": h2,
            "sectionTitle": h2.split(". ", 1)[1] if ". " in h2 else h2,
            "display": display,
            "codes": tokens,
            "nums": numeric_alias(tokens),
            "cause": cause,
            "check": check,
            "steps": split_steps(check),
            "category": category_of(cause, h2),
            "reset": RESET[brand],
            "kind": "code",
            "isLamp": first == "표시",
        })

# 제조사 현장 노트 (각 장 마지막 '점검 포인트' 절)
note_map = {"1-8": "samsung", "2-5": "lg", "3-7": "carrier", "4-3": "winia"}
cur = None
for b in content.BLOCKS:
    if b["t"] == "h2":
        key = b["text"].split(".")[0]
        cur = note_map.get(key)
        if cur:
            brand_notes.setdefault(cur, [])
    elif b["t"] == "li" and cur:
        brand_notes[cur].append(b["text"])
    elif b["t"] in ("h1", "body", "table"):
        cur = None if b["t"] == "h1" else cur

# 부록 C 안전 원칙
in_safety = False
for b in content.BLOCKS:
    if b["t"] == "h1":
        in_safety = b["text"].startswith("부록 C")
    elif b["t"] == "li" and in_safety:
        safety.append(b["text"])

# LG PCB 항목에 점검 포인트 보강(6-4 본문·2장 표에서 같은 코드 찾기)
by_code = {}
for e in entries:
    for c in e["codes"]:
        by_code.setdefault(norm(c), e)
for p in led["lgPcb"]:
    e = by_code.get(norm(p["code"]))
    if e:
        p["check"] = e["check"]
        p["device"] = e["device"]
        p["cause"] = e["cause"] or p["cause"]
    p["reset"] = RESET["lg"]

# 고객센터: 부록 B 순서를 기본으로 하고, 7-6에만 있는 항목을 뒤에 붙인다
centers = list(centers_b)
_seen = set(c["maker"].split("(")[0].split("·")[0].strip() for c in centers)
for c in centers_fcu:
    base = c["maker"].split("(")[0].strip()
    if base not in _seen:
        centers.append(c)
        _seen.add(base)

data = {
    "meta": {
        "title": "에어컨 에러코드 조회",
        "subtitle": "삼성 · LG · 캐리어 · 위니아 · 파세코 · FCU",
        "academy": "최정예홈케어아카데미",
        "brand": "쾌적하마",
        "academyUrl": "https://cjyacademy.com",
        "updated": "2026-11-17",
        "source": "제조사 공식 고객지원·사용설명서 확인 기준",
    },
    "brands": [{"id": b, **BRANDS[b]} for b in BRAND_ORDER],
    "entries": entries,
    "led": led,
    "brandNotes": brand_notes,
    "centers": centers,
    "checklist": checklist,
    "safety": safety,
    "reset": RESET,
}

# 통계
stats = {}
for e in entries:
    stats[e["brand"]] = stats.get(e["brand"], 0) + 1
data["meta"]["count"] = len(entries)
data["meta"]["codeCount"] = sum(1 for e in entries if e["kind"] == "code")
data["meta"]["ledCount"] = sum(1 for e in entries if e["kind"] == "led")
data["meta"]["stats"] = stats

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "aircon_codes.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=1)

print("entries:", len(entries), stats)
print("LED lgPcb:", len(led["lgPcb"]), "cassette:", len(led["cassette"]), "carrierLamp:", len(led["carrierLamp"]))
print("checklist:", len(checklist), "centers:", len(centers), "notes:", {k: len(v) for k, v in brand_notes.items()})
print("unknown tables:", unknown_tables)
print("intro tables:", [(i, h) for i, h1_, h, c in intro_tables])
print("bytes:", os.path.getsize(out))
