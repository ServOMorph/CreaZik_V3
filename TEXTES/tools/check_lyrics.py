"""Contrôle un fichier de paroles balisées pour ACE-Step 1.5 avant génération. Ne modifie jamais le fichier."""
import argparse
import re
import sys
from pathlib import Path

ALLOWED_TAGS = {
    "intro", "verse", "pre-chorus", "chorus", "bridge", "outro", "final chorus",
    "build", "drop", "breakdown", "instrumental", "guitar solo", "piano interlude", "fade out", "silence",
    "raspy vocal", "whispered", "falsetto", "powerful belting", "spoken word", "harmonies", "call and response", "ad-lib",
    "high energy", "low energy", "building energy", "explosive", "melancholic", "euphoric", "dreamy", "aggressive",
    "drum break", "explosive drop",
}
NO_LYRICS_OK = {
    "intro", "outro", "build", "drop", "breakdown", "instrumental", "guitar solo", "piano interlude", "fade out",
    "silence", "drum break", "explosive drop", "building energy", "low energy", "high energy",
}
MAX_DURATION_S = 135
VOWELS = "aeiouyàâäéèêëîïôöùûüÿœæ"
SECONDS_PER_LINE = 2.5
SECONDS_PER_SECTION = 3.0


ENT_SOUNDED = {
    "content", "souvent", "présent", "absent", "argent", "serpent", "torrent", "parent", "excellent",
    "innocent", "violent", "patient", "différent", "évident", "urgent", "récent", "prudent", "puissant",
}


def mute_ent(w):
    return w.endswith("ent") and len(w) > 4 and not w.endswith("ment") and w not in ENT_SOUNDED


def syllables(line):
    total = 0
    for w in re.findall(r"[a-zàâäéèêëîïôöùûüÿœæç]+", line.lower()):
        w = re.sub(r"q[u]", "q", w)
        n = len(re.findall(f"[{VOWELS}]+", w))
        if n > 1 and (w.endswith("e") or w.endswith("es") or mute_ent(w)):
            n -= 1
        total += n
    return total


def parse_sections(lines):
    sections = []
    for i, raw in enumerate(lines, 1):
        s = raw.strip()
        if re.match(r"^\[[^\]]*\]", s):
            sections.append({"tag": s, "line": i, "text": []})
        elif s and sections:
            sections[-1]["text"].append((i, s))
    return sections


def check(path, caption, duration, max_syll, hard_syll):
    findings = []

    def add(level, line, msg):
        findings.append((level, line, msg))

    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        add("ERREUR", 0, "le fichier n'est pas en UTF-8")
        return findings
    if raw.startswith(b"\xef\xbb\xbf"):
        add("AVERT", 1, "BOM UTF-8 en début de fichier")
    if "�" in text or re.search(r"Ã[\x80-\xbf©¨ª]", text):
        add("ERREUR", 0, "caractères corrompus (encodage), accents à vérifier")
    if "\r" in text:
        add("AVERT", 0, "fins de ligne CRLF, préférer LF")
    lines = text.split("\n")

    first_content = next((i for i, l in enumerate(lines, 1) if l.strip()), None)
    if first_content is None:
        add("ERREUR", 0, "fichier vide")
        return findings
    if not lines[first_content - 1].strip().startswith("["):
        add("ERREUR", first_content, "du texte avant la première balise de section")

    sections = parse_sections(lines)
    if not sections:
        add("ERREUR", 0, "aucune balise de section")
        return findings

    for i, raw_line in enumerate(lines, 1):
        s = raw_line.strip()
        m = re.match(r"^\[([^\]]*)\](.*)$", s)
        if m and m.group(2).strip():
            add("ERREUR", i, "la balise doit être seule sur sa ligne : " + s[:50])
        elif "[" in s and "]" in s and not m:
            add("AVERT", i, "balise au milieu d'une ligne de texte : " + s[:50])

    for k, sec in enumerate(sections):
        m = re.match(r"^\[([^\]]*)\]", sec["tag"])
        inner = m.group(1).strip()
        base, _, desc = inner.partition(" - ")
        base_l = re.sub(r"\s+\d+$", "", base.strip().lower())
        if base_l not in ALLOWED_TAGS:
            add("AVERT", sec["line"], f"balise inconnue [{inner}]")
        if desc and len(desc.split()) > 2:
            add("AVERT", sec["line"], f"descripteur trop long ({len(desc.split())} mots) : le modèle peut le chanter")
        if not sec["text"]:
            if base_l in NO_LYRICS_OK:
                add("INFO", sec["line"], f"section sans paroles [{inner}] : la doc ACE l'emploie pour un passage instrumental, effet non testé dans ce projet")
            else:
                add("ERREUR", sec["line"], f"section vide [{inner}] : une section de chant sans paroles")
        if k > 0 and sec["line"] >= 2 and lines[sec["line"] - 2].strip():
            add("AVERT", sec["line"], "pas de ligne vide avant la balise")

    n_lines = 0
    counts = []
    for sec in sections:
        for i, s in sec["text"]:
            n_lines += 1
            n = syllables(s)
            counts.append(n)
            if n > hard_syll:
                add("AVERT", i, f"environ {n} syllabes (> {hard_syll}) : le rythme se brise, à réécrire ou couper : {s[:60]}")
            elif n > max_syll:
                add("AVERT", i, f"environ {n} syllabes (> {max_syll}) : {s[:60]}")
            if len(s) > 80:
                add("AVERT", i, "ligne très longue en caractères")

    if duration and duration > MAX_DURATION_S:
        add("AVERT", 0, f"durée de {duration} s : rester à {MAX_DURATION_S} s ou moins (blocages de décodage constatés au-delà)")
    est = n_lines * SECONDS_PER_LINE + len(sections) * SECONDS_PER_SECTION
    if duration and est > duration:
        add("AVERT", 0, f"{n_lines} lignes et {len(sections)} sections : environ {est:.0f} s à {SECONDS_PER_LINE} s par ligne (estimation grossière, non mesurée) pour {duration} s demandées")

    if caption:
        terms = [t.strip() for t in caption.split(",") if t.strip()]
        low = caption.lower()
        if not 5 <= len(terms) <= 12:
            add("AVERT", 0, f"caption de {len(terms)} termes (5 à 12 conseillés)")
        if re.search(r"\b\d{2,3}\s*bpm\b", low) or re.search(r"\b[a-g][#b]?\s*(major|minor)\b", low):
            add("AVERT", 0, "tempo ou tonalité dans le caption : la doc ACE conseille les paramètres bpm et keyscale")
        if re.search(r"(?<!non )(?<!non-)(?<!not )\binstrumental\b", low) and n_lines:
            add("ERREUR", 0, "caption instrumental mais des paroles sont fournies")
        if "no vocals" in low and n_lines:
            add("ERREUR", 0, "caption sans voix mais des paroles sont fournies")
        if ("spoken word" in low or "slam" in low) and not any("spoken word" in s["tag"].lower() for s in sections):
            add("AVERT", 0, "caption parlé ou slam sans balise [spoken word] dans les paroles")
        if "female" in low and "male vocal" in low.replace("female", ""):
            add("AVERT", 0, "caption avec voix féminine et masculine : confirmer que c'est voulu")

    stats = f"{len(sections)} sections, {n_lines} lignes, syllabes par ligne : min {min(counts, default=0)}, max {max(counts, default=0)}, moyenne {sum(counts) / max(1, len(counts)):.1f} (comptage approximatif)"
    return findings, stats


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("fichier")
    p.add_argument("--caption", default="")
    p.add_argument("--duree", type=int, default=0, help="durée visée en secondes")
    p.add_argument("--max-syll", type=int, default=10)
    p.add_argument("--max-syll-dur", type=int, default=12)
    a = p.parse_args()
    path = Path(a.fichier)
    if not path.is_file():
        print(f"ERREUR : fichier introuvable : {path}")
        return 2
    res = check(path, a.caption, a.duree, a.max_syll, a.max_syll_dur)
    findings, stats = res if isinstance(res, tuple) else (res, "")
    for level, line, msg in sorted(findings, key=lambda f: (f[0] != "ERREUR", f[1])):
        print(f"{level}{' ligne ' + str(line) if line else ''} : {msg}")
    if stats:
        print(stats)
    errors = sum(1 for f in findings if f[0] == "ERREUR")
    warns = sum(1 for f in findings if f[0] == "AVERT")
    print(f"Résultat : {errors} erreur(s), {warns} avertissement(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
