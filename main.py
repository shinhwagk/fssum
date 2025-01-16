import argparse
import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Generator


def get_datetime():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hash_file(f: str, chunk_size: int = 8192) -> str:
    shasum = hashlib.sha256()
    with open(f, "rb") as fio:
        while chunk := fio.read(chunk_size):
            shasum.update(chunk)
    return shasum.hexdigest()


def list_all_files(dir_path: str) -> Generator[str, Any, None]:
    for root, _, filenames in os.walk(dir_path):
        for filename in filenames:
            yield os.path.join(root, filename)


def read_shasum(_f: str) -> dict[str, str]:
    with open(_f, "r", encoding="utf8") as f:
        return json.load(f)


def write_shasum(_f: str, shasum: dict[str, str]):
    with open(_f, "w", encoding="utf8") as f:
        return json.dump(shasum, f)


@dataclass
class ParseArgs:
    shasum_dir: str
    shasum_file: str
    shasum_force: bool


def parse_args() -> ParseArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shasum-dir", type=str, required=True)
    parser.add_argument("--shasum-file", type=str, required=True)
    parser.add_argument("--shasum-force", action="store_true", default=False)
    args = parser.parse_args()
    return ParseArgs(**vars(args))


def main():
    args = parse_args()

    files_shasum: dict[str, str] = dict()
    if os.path.exists(args.shasum_file):
        files_shasum = read_shasum(args.shasum_file)

    for f in list_all_files(args.shasum_dir):
        if args.shasum_force or f not in files_shasum:
            print(f"file:{f}, shasum...")
            files_shasum[f] = {"shasum": hash_file(f), "date": get_datetime()}
            print(f"file:{f}, shasum complate.")
        else:
            print(f"file:{f}, shasum skip.")

    write_shasum(args.shasum_file, files_shasum)


# python main.py --shasum-dir abc --shasum-file xxx.json

if __name__ == "__main__":
    main()
