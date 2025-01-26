import argparse
import concurrent.futures
import hashlib
import json
import multiprocessing
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Generator


@dataclass
class ShasumConfig:
    shasum_dir: str
    shasum_sample: int


@dataclass
class ShasumData:
    config: ShasumConfig
    files: dict[str, str]


@dataclass
class ParseArgs:
    shasum_file: str
    shasum_force: bool


def get_datetime():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hashCore(f: str, sample: int = 100) -> str:
    """sample 100 mb"""
    shasum = hashlib.sha256()
    fstat = os.stat(f)
    sampleThreshold = 1024 * 1024 * sample
    with open(f, "rb") as fio:
        if fstat.st_size < sampleThreshold:
            shasum.update(fio.read())
        else:
            step = int(fstat.st_size / sampleThreshold)
            stepSize = int(fstat.st_size / step)
            for i in range(0, step - 1):
                fio.seek(i * stepSize)
                shasum.update(fio.read(1))
            fio.seek(-1, os.SEEK_END)
            shasum.update(fio.read())
        return shasum.hexdigest()


def list_all_files(dir_path: str) -> Generator[str, Any, None]:
    for root, _, filenames in os.walk(dir_path):
        for filename in filenames:
            yield os.path.join(root, filename)


def read_shasum_file(_f: str) -> ShasumData:
    with open(_f, "r", encoding="utf8") as f:
        data: dict = json.load(f)
        return ShasumData(config=ShasumConfig(**data["config"]), files=data.get("files", {}))


def write_shasum(_f: str, shasum_data: ShasumData):
    with open(_f, "w", encoding="utf8") as f:
        json.dump(asdict(shasum_data), f, ensure_ascii=False, indent=4)


def parse_args() -> ParseArgs:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shasum-file", type=str, required=True)
    parser.add_argument("--shasum-force", action="store_true", default=False)
    args = parser.parse_args()
    return ParseArgs(**vars(args))


def main():
    args = parse_args()

    if not os.path.exists(args.shasum_file):
        raise Exception("xxx")

    shasum_data = read_shasum_file(args.shasum_file)

    success_cnt = 0

    futures: dict[concurrent.futures.Future, str] = {}
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for f in list_all_files(shasum_data.config.shasum_dir):
            if f == args.shasum_file or (not args.shasum_force and f in shasum_data.files):
                print(f"skip {f}")
                continue

            future = executor.submit(hashCore, f)
            futures[future] = f

            if len(futures) >= multiprocessing.cpu_count():
                completed, _ = concurrent.futures.wait(futures.keys(), return_when=concurrent.futures.FIRST_COMPLETED)

                for fut in completed:
                    file_sumsha = fut.result()
                    shasum_data.files[futures[fut]] = {"shasum": file_sumsha, "date": get_datetime()}
                    print(f"shasum {file_sumsha} {futures[fut]}")

                    del futures[fut]
                    success_cnt += 1

            if success_cnt % 100 == 0:
                pass
                # write_shasum(args.shasum_file, shasum_data)

        for fut in concurrent.futures.as_completed(futures.keys()):
            file_sumsha = fut.result()
            shasum_data.files[futures[fut]] = {"shasum": file_sumsha, "date": get_datetime()}
            print(f"shasum {file_sumsha} {futures[fut]}")

    write_shasum(args.shasum_file, shasum_data)


if __name__ == "__main__":
    main()
