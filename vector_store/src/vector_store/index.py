"""One-time bulk indexing: walk a file or directory, split content into
fixed-size overlapping chunks, embed each via llama.cpp, store in the
configured vector backend (default: Qdrant).

No format-specific parsing - this works the same for a markdown file, a repo
full of YAML, source code, or any other text content. Each chunk is prefixed
with its file path so near-identical files (e.g. many similar config files)
stay distinguishable to the embedding model. If the target is a git repo,
.gitignore rules (via `git ls-files`) are respected so build artifacts,
dependencies, etc. never get indexed.
"""
import argparse
import pathlib
import subprocess
import uuid

import requests

from .embedding import embed_document
from .vectorstore import get_backend

def _default_source_file() -> pathlib.Path:
    """Walk up from this file looking for a test_data/ dir, instead of
    hardcoding how many levels up the repo root is."""
    for parent in pathlib.Path(__file__).resolve().parents:
        candidate = parent / "test_data" / "sample_texts.md"
        if candidate.exists():
            return candidate
    return pathlib.Path("test_data/sample_texts.md")


DEFAULT_SOURCE_FILE = _default_source_file()

# The nomic-embed GGUF used here has a hard 2048-token context limit. ~2.9
# chars/token was measured against this model's tokenizer, so this is a
# conservative char budget per chunk, leaving room for the path header and
# the "search_document: " prefix added at embed time.
CHUNK_CHARS = 4000
CHUNK_OVERLAP_CHARS = 400

# Fallback skip-list used only when the target isn't a git repo, so
# .gitignore can't be consulted.
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "dist", "build"}
SKIP_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".pdf",
    ".zip", ".tar", ".gz", ".whl", ".pyc", ".lock",
}


def _git_tracked_files(root: pathlib.Path) -> list[pathlib.Path] | None:
    """Files git would track or allow, respecting .gitignore. None if `root`
    isn't inside a git work tree."""
    check = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
        capture_output=True, text=True,
    )
    if check.returncode != 0:
        return None
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard"],
        capture_output=True, text=True, check=True,
    )
    return [root / line for line in result.stdout.splitlines() if line]


def iter_source_files(path: pathlib.Path):
    if path.is_file():
        yield path
        return

    tracked = _git_tracked_files(path)
    if tracked is not None:
        for file_path in sorted(tracked):
            if file_path.is_file() and file_path.suffix.lower() not in SKIP_SUFFIXES:
                yield file_path
        return

    for file_path in sorted(path.rglob("*")):
        if not file_path.is_file():
            continue
        if file_path.suffix.lower() in SKIP_SUFFIXES:
            continue
        if SKIP_DIRS & set(file_path.relative_to(path).parts):
            continue
        yield file_path


def split_into_chunks(text: str) -> list[str]:
    if len(text) <= CHUNK_CHARS:
        return [text]
    chunks = []
    start = 0
    step = CHUNK_CHARS - CHUNK_OVERLAP_CHARS
    while start < len(text):
        chunks.append(text[start : start + CHUNK_CHARS])
        start += step
    return chunks


def load_chunks(path: pathlib.Path) -> list[dict]:
    chunks = []
    root = path if path.is_dir() else path.parent
    for file_path in iter_source_files(path):
        try:
            body = file_path.read_text().strip()
        except (UnicodeDecodeError, OSError):
            continue
        if not body:
            continue
        relative_path = file_path.relative_to(root)
        for i, piece in enumerate(split_into_chunks(body)):
            text = f"File: {relative_path}\n\n{piece}"
            chunks.append(
                {
                    "text": text,
                    "topic": f"{relative_path.stem} [{i}]" if i else relative_path.stem,
                    "source": str(file_path),
                }
            )
    return chunks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "source_file",
        nargs="?",
        type=pathlib.Path,
        default=DEFAULT_SOURCE_FILE,
        help="File or directory to index (default: test_data/sample_texts.md)",
    )
    args = parser.parse_args()

    backend = get_backend()
    chunks = load_chunks(args.source_file)
    print(f"Indexing {len(chunks)} chunks from {args.source_file}")

    skipped = 0
    for chunk in chunks:
        try:
            vector = embed_document(chunk["text"])
        except requests.exceptions.HTTPError as e:
            print(f"  SKIPPED [{chunk['topic']}]: {e}")
            skipped += 1
            continue
        backend.upsert(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "text": chunk["text"],
                "topic": chunk["topic"],
                "source": chunk["source"],
            },
        )
        print(f"  stored [{chunk['topic']}] {chunk['text'][:60]}...")

    print(f"Done. {skipped} chunk(s) skipped due to embedding errors.")


if __name__ == "__main__":
    main()
