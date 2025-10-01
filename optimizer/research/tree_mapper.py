import csv, hashlib, json, os, pathlib, sys, time, io
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
import yaml
from datetime import datetime, timezone

# Optional Mission Ω lineage (no-op if absent)
try:
    from optimizer.mutationanchor import MutationAnchor  # type: ignore
except Exception:  # pragma: no cover
    class MutationAnchor:  # minimal stub
        def record(self, kind: str, payload: dict, parent_id: Optional[str]=None):
            return type("E", (), {"event_id": f"ev-{int(time.time())}"})

# Optional pathspec ignore support
try:
    from pathspec import PathSpec
except Exception as e:  # pragma: no cover
    PathSpec = None  # type: ignore

ROOT = pathlib.Path(__file__).resolve().parents[2]
CFG  = ROOT / "optimizer" / "research" / "tree_config.yaml"
OUTD = ROOT / "docs" / "tree"
OUTD.mkdir(parents=True, exist_ok=True)

FILES_JSONL = OUTD / "files.jsonl"
DIRS_JSON   = OUTD / "dirs.json"
TREE_MD     = OUTD / "TREE.md"
SUMMARY_CSV = OUTD / "summary.csv"
INDEX_MD    = OUTD / "README.md"

@dataclass
class FileRec:
    path: str             # posix path from repo root
    size_bytes: int
    lines: int
    lang: str
    sha256: str
    mtime_iso: str
    preview: Optional[str] = None

EXT_LANG = {
    ".py":"python",".ts":"typescript",".tsx":"typescript",".js":"javascript",
    ".jsx":"javascript",".md":"markdown",".yml":"yaml",".yaml":"yaml",
    ".json":"json",".toml":"toml",".ini":"ini",".cfg":"ini",".sh":"bash",
    ".bash":"bash",".zsh":"bash",".go":"go",".rs":"rust",".cpp":"cpp",
    ".cc":"cpp",".c":"c",".h":"c",".hpp":"cpp",".sql":"sql",".html":"html",
    ".css":"css",".scss":"css",".svg":"svg",".txt":"text",".log":"text",
    ".ipynb":"jupyter",".java":"java",".kt":"kotlin",".rb":"ruby",".php":"php",
}

BINARY_EXT = {".png",".jpg",".jpeg",".gif",".webp",".ico",".pdf",".bin",".onnx",".pt",".pth",".tflite",".wasm",".zip",".gz",".tar",".xz",".7z",".parquet"}

def _load_cfg() -> dict:
    if CFG.exists():
        return yaml.safe_load(CFG.read_text(encoding="utf-8")) or {}
    return {}

def _lang_for(p: pathlib.Path) -> str:
    return EXT_LANG.get(p.suffix.lower(), "binary" if p.suffix.lower() in BINARY_EXT else "text")

def _is_text(p: pathlib.Path) -> bool:
    return p.suffix.lower() not in BINARY_EXT

def _sha256(path: pathlib.Path, limit_mb: Optional[int]=None) -> str:
    h = hashlib.sha256()
    max_bytes = None if limit_mb is None else limit_mb * 1024 * 1024
    with path.open("rb") as f:
        read = 0
        while True:
            chunk = f.read(1024*1024)
            if not chunk: break
            read += len(chunk)
            h.update(chunk)
            if max_bytes is not None and read >= max_bytes:
                break
    return h.hexdigest()

def _count_lines(path: pathlib.Path) -> int:
    if not _is_text(path):
        return 0
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def _preview(path: pathlib.Path, max_bytes: int) -> Optional[str]:
    if not _is_text(path): return None
    try:
        b = path.read_bytes()[:max_bytes]
        return b.decode("utf-8", errors="ignore")
    except Exception:
        return None

def _should_exclude(rel: pathlib.Path, spec, excludes: List[str]) -> bool:
    s = str(rel.as_posix())
    if spec and spec.match_file(s):
        return True
    # glob-ish excludes
    for pat in excludes:
        # simple "**" + startswith check
        if pat.endswith("/**") and s.startswith(pat[:-3]):
            return True
        if pat.strip("*") and pat.replace("**","") in s and pat.startswith("*"):
            return True
    return False

def _collect(cfg: dict) -> Tuple[List[FileRec], Dict[str, dict]]:
    excludes = cfg.get("exclude_globs", [])
    # respect .gitignore if pathspec is available
    spec = None
    gi = ROOT / ".gitignore"
    if PathSpec and gi.exists():
        spec = PathSpec.from_lines("gitwildmatch", gi.read_text().splitlines())

    hash_large = bool(cfg.get("hash_large_files", True))
    hash_limit = int(cfg.get("hash_max_mb", 50))
    do_preview = bool(cfg.get("store_preview", True))
    prev_bytes = int(cfg.get("preview_max_bytes", 512))

    files: List[FileRec] = []
    dir_agg: Dict[str, dict] = {}

    for path in sorted(ROOT.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(ROOT)
        if _should_exclude(rel, spec, excludes):
            continue
        try:
            stat = path.stat()
        except FileNotFoundError:
            continue
        size = stat.st_size
        lang = _lang_for(path)
        sha = _sha256(path, None if hash_large else hash_limit)
        lines = _count_lines(path)
        mt = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat()
        prev = _preview(path, prev_bytes) if do_preview and size <= 2*1024*1024 else None

        rec = FileRec(
            path=rel.as_posix(),
            size_bytes=size,
            lines=lines,
            lang=lang,
            sha256=sha,
            mtime_iso=mt,
            preview=prev
        )
        files.append(rec)

        parent = rel.parent.as_posix() if rel.parent.as_posix() != "" else "."
        agg = dir_agg.setdefault(parent, {"files":0, "bytes":0, "lines":0})
        agg["files"] += 1
        agg["bytes"] += size
        agg["lines"] += lines

    return files, dir_agg

def _render_tree(files: List[FileRec]) -> str:
    # Build a directory tree with lightweight metadata
    from collections import defaultdict
    tree = defaultdict(list)
    for fr in files:
        parts = fr.path.split("/")
        dirp = "/".join(parts[:-1]) if len(parts)>1 else "."
        tree[dirp].append(fr)

    def listdir(d: str) -> List[str]:
        children = sorted({p.split("/")[0] for p in {dp for dp in tree if dp.startswith(d + "/")} })
        return children

    # Build a pretty tree by walking from root
    lines = ["# Repository File Tree", ""]
    # index directories for traversal
    dirs = sorted({p for p in tree} | {"."})
    # Simple pretty tree
    def fmt_file(fr: FileRec) -> str:
        kb = fr.size_bytes/1024
        return f"{fr.path}  ({int(kb)} KB, {fr.lines} ln, {fr.lang})"

    for fr in sorted(files, key=lambda x: x.path):
        indent = "  " * (fr.path.count("/"))
        name = fr.path.split("/")[-1]
        kb = fr.size_bytes/1024
        lines.append(f"{indent}- {name}  _{int(kb)} KB • {fr.lines} ln • {fr.lang}_")

    return "\n".join(lines) + "\n"

def _render_index(files: List[FileRec], dir_agg: Dict[str, dict]) -> str:
    total_b = sum(fr.size_bytes for fr in files)
    total_l = sum(fr.lines for fr in files)
    return "\n".join([
        "# File Atlas",
        "",
        f"- files: {len(files)}",
        f"- total size: {total_b/1024:.1f} KB",
        f"- total lines (text only): {total_l}",
        "",
        "Artifacts:",
        "- `docs/tree/TREE.md` — pretty tree",
        "- `docs/tree/files.jsonl` — per-file records (path, size, lines, lang, sha256, mtime, preview)",
        "- `docs/tree/summary.csv` — spreadsheet-friendly snapshot",
        "- `docs/tree/dirs.json` — per-directory aggregates",
        ""
    ])

def _write(files: List[FileRec], dir_agg: Dict[str, dict]) -> None:
    # JSONL
    with FILES_JSONL.open("w", encoding="utf-8") as f:
        for fr in files:
            f.write(json.dumps(asdict(fr), ensure_ascii=False) + "\n")
    # CSV
    with SUMMARY_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["path","size_bytes","lines","lang","sha256","mtime_iso"])
        for fr in files:
            w.writerow([fr.path, fr.size_bytes, fr.lines, fr.lang, fr.sha256, fr.mtime_iso])
    # DIRS
    DIRS_JSON.write_text(json.dumps(dir_agg, indent=2), encoding="utf-8")
    # TREE
    TREE_MD.write_text(_render_tree(files), encoding="utf-8")
    # INDEX
    INDEX_MD.write_text(_render_index(files, dir_agg), encoding="utf-8")

def _apply_manifest(files: List[FileRec], cfg: dict) -> None:
    manifest_file = cfg.get("manifest_file")
    if not manifest_file:
        return
    mfpath = ROOT / manifest_file
    if not mfpath.exists():
        return
    mf = yaml.safe_load(mfpath.read_text(encoding="utf-8")) or {}
    maps = mf.get("mappings", [])
    if not maps:
        return
    # annotate preview with remap hint
    lookup = {(m.get("to") or "").strip(): (m.get("from") or "").strip() for m in maps if m.get("to") and m.get("from")}
    for fr in files:
        if fr.path in lookup:
            hint = f"[moved from: {lookup[fr.path]}]\n"
            fr.preview = (hint + (fr.preview or ""))[:512]

def main():
    cfg = _load_cfg()
    files, dir_agg = _collect(cfg)
    _apply_manifest(files, cfg)
    _write(files, dir_agg)
    # lineage event
    anchor = MutationAnchor()
    ev = anchor.record(kind="file_tree_map", payload={
        "files": len(files),
        "dirs": len(dir_agg),
        "outputs": ["docs/tree/TREE.md","docs/tree/files.jsonl","docs/tree/summary.csv","docs/tree/dirs.json"],
        "ts": time.time(),
    })
    print(f"File Atlas written. event_id={getattr(ev,'event_id','')}")
if __name__ == "__main__":
    main()