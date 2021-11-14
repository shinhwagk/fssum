#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import hashlib

sampleThreshold = 128 * 1024


def hashCore(fstat, fio):
    shasum = hashlib.sha256()
    if fstat.st_size < sampleThreshold:
        shasum.update(fio.read())
    else:
        stepSize = int(fstat.st_size / step)
        for i in range(0, step-1):
            fio.seek(i*stepSize)
            shasum.update(fio.read(1))
        fio.seek(-1, os.SEEK_END)
        shasum.update(fio.read())
    return shasum.hexdigest()


def main():
    if len(sys.argv) > 1:
        fstat = os.stat(sys.argv[1])
        with open(sys.argv[1], 'rb') as fio:
            print(hashCore(fstat, fio))


if __name__ == "__main__":
    step = int(os.getenv('fssum_step') or "8")
    main()
