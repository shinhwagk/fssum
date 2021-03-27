#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import sys
import hashlib

sampleSize = 16 * 1024
sampleThreshold = 128 * 1024


def medianOffset(fsize):
    rsize = 0
    offset = sampleSize
    if fsize % 2 == 0:
        rsize = fsize / 2 - sampleSize / 2
    else:
        rsize = (fsize - 1) / 2 - sampleSize / 2
        offset += 1
    return (int(rsize), offset)


def hashCore(fstat, fio):
    shasum = hashlib.sha256()
    if fstat.st_size < sampleThreshold:
        shasum.update(fio.read())
    else:
        shasum.update(fio.read(sampleSize))
        (r, o) = medianOffset(fstat.st_size)
        fio.seek(r)
        shasum.update(fio.read(o))
        fio.seek(-1*sampleSize, os.SEEK_END)
        shasum.update(fio.read())
    return shasum.hexdigest()


def main():
    try:
        if len(sys.argv) > 1:
            fstat = os.stat(sys.argv[1])
            with open(sys.argv[1], 'rb') as fio:
                print(hashCore(fstat, fio))
    except BaseException as e:
        print(e)


if __name__ == "__main__":
    main()
