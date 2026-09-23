"""AnkiTXT 核心逻辑：TXT → APKG"""
import re
from pathlib import Path
import genanki

MODEL_ID = 1607392320
DECK_ID  = 2059400113

CSS = """
.card {
    font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 18px;
    color: #24292e;
    background: #fdfdfd;
    line-height: 1.75;
    padding: 20px;
}
.front { font-weight: 600; font-size: 20px; margin-bottom: 12px; white-space: pre-wrap; }
.back  { color: #24292e; white-space: pre-wrap; }
hr#answer { border: none; border-top: 1px dashed #ccc; margin: 16px 0; }
"""

_MODEL = genanki.Model(
    MODEL_ID, "TXT2APKG Model",
    fields=[{"name": "Front"}, {"name": "Back"}],
    templates=[{
        "name": "Basic",
        "qfmt": '<div class="front">{{Front}}</div>',
        "afmt": '<div class="front">{{Front}}</div>'
                '<hr id="answer"><div class="back">{{Back}}</div>',
    }],
    css=CSS,
)


def _detect_delimiter(text):
    lines = [l for l in text.split("\n") if l.strip()]
    if not lines:
        return None
    for d in ["\t", ":::", "|||", "||", " | ", "===", "|", " —— "]:
        hits = sum(1 for l in lines if d in l)
        if hits >= max(1, len(lines) * 0.6):
            return d
    return None


def _parse_delimited(text, delim):
    cards = []
    for line in text.split("\n"):
        line = line.rstrip("\r")
        if not line.strip() or delim not in line:
            continue
        front, _, back = line.partition(delim)
        front, back = front.strip(), back.strip()
        if front:
            cards.append((front, back))
    return cards


def _parse_qa_blocks(text):
    blocks = re.split(r"\n(?=\s*[Qq][:：.、])", text)
    cards = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        m = re.match(
            r"\s*[Qq][:：.、]\s*(.*?)\n\s*[Aa][:：.、]\s*(.*)",
            block, re.S
        )
        if m:
            front = m.group(1).strip()
            back = m.group(2).strip()
            if front:
                cards.append((front, back))
    return cards


def _parse_blocks(text):
    cards = []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block:
            continue
        lines = block.split("\n")
        front = lines[0].strip()
        back = "\n".join(lines[1:]).strip()
        if front:
            cards.append((front, back))
    return cards


def parse_txt(text, delimiter=None):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if delimiter:
        d = "\t" if delimiter == "\\t" else delimiter
        return _parse_delimited(text, d)
    if re.search(r"^\s*[Qq][:：.、]", text, re.M):
        cards = _parse_qa_blocks(text)
        if cards:
            return cards
    d = _detect_delimiter(text)
    if d:
        cards = _parse_delimited(text, d)
        if cards:
            return cards
    return _parse_blocks(text)


def build_apkg(cards, output, deck_name):
    out = Path(output).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    deck = genanki.Deck(DECK_ID, deck_name)
    for front, back in cards:
        deck.add_note(genanki.Note(model=_MODEL, fields=[front, back]))
    genanki.Package(deck).write_to_file(str(out))
    return len(cards)


def build_merged_apkg(grouped, parent_name, output):
    out = Path(output).expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    package = genanki.Package([])
    total = 0
    base_id = 2059400200
    for i, (sub_name, cards) in enumerate(grouped.items()):
        deck = genanki.Deck(base_id + i, f"{parent_name}::{sub_name}")
        for front, back in cards:
            deck.add_note(genanki.Note(model=_MODEL, fields=[front, back]))
            total += 1
        package.decks.append(deck)
    package.write_to_file(str(out))
    return total


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python core.py 输入.txt")
        sys.exit(1)
    src = Path(sys.argv[1]).expanduser()
    text = src.read_text(encoding="utf-8")
    cards = parse_txt(text)
    n = build_apkg(cards, src.with_suffix(".apkg"), src.stem)
    print(f"✅ {n} 张卡片 → {src.with_suffix('.apkg')}")
