import os
import hashlib
import numpy as np
 
def checkDir(directory, unique = False):
    if directory[-1] == '/':
        directory = directory[:-1]
    if not os.path.exists(directory):
        os.makedirs(directory)
        return directory
        
    if unique:
        suffix = 1
        while os.path.exists("{}_{}".format(directory,suffix)):
            suffix += 1
        os.mkdir("{}_{}".format(directory,suffix))
        return "{}_{}".format(directory,suffix)

    return directory

def fastHash(fileName):
    if not os.path.isfile(fileName):
        print("Helpers - FastHash: File {} not found!".format(fileName))
        return ''
    
    BLOCKSIZE = 16 * 1024

    fileSize = fileSize = os.path.getsize(fileName)
    hasher = hashlib.sha256()

    with open(fileName, 'rb') as inFile:
        if fileSize < 1024 * 1024:
            hasher.update(inFile.read())
        else:
            hasher.update(inFile.read(BLOCKSIZE))
            for iBlock in range(1,9):
                inFile.seek(int(fileSize/10) * iBlock, 0)
                hasher.update(inFile.read(BLOCKSIZE))
            inFile.seek(-BLOCKSIZE, os.SEEK_END)
            hasher.update(inFile.read(BLOCKSIZE))
            hasher.update(str(fileSize).encode('utf-8'))

    return hasher.hexdigest()

def sha256Hash(fileName):
    if not os.path.isfile(fileName):
        print("Helpers - sha256Hash: File {} not found!".format(fileName))
        return ''
    
    BLOCKSIZE = 16 * 1024
    hasher = hashlib.sha256()

    with open(fileName, 'rb') as inFile:
        for block in iter(lambda: inFile.read(BLOCKSIZE), b''):
            hasher.update(block)

    return hasher.hexdigest()

def checkFileSize(fileName, nrTraces, length, dtype):
    dtype = np.dtype(dtype)
    fileSize = os.path.getsize(fileName)
    arraySize = dtype.itemsize * nrTraces * length
    if not fileSize == (arraySize):
        return False
    return True

def getSpareBytes(fileName, nrTraces, length, dtype):
    spareBytes = 0
    fileSize = os.path.getsize(fileName)
    arraySize = dtype.itemsize * nrTraces * length
    if not fileSize == (arraySize):
        print("Warning: Size of {} ({}) and size of array ({} * {} * {} = {}) do not match!".\
            format(fileName,fileSize,dtype.itemsize, nrTraces, length, arraySize))
        if fileSize < arraySize: raise ValueError("Size missmatch! File size < array size")
        else:
            if ((fileSize - arraySize) % nrTraces) == 0:
                spareBytes = int((fileSize - arraySize) / nrTraces)
                print("Found exactly {} additional byte(s) per Trace (EOL char?).".format(spareBytes))
                print("Adding them to # of sample points")
    return spareBytes

def getMaximumTracesInFile(fileName, length, dtype):
    fileSize = os.path.getsize(fileName)
    traceSize = dtype.itemsize * length
    if not (fileSize % traceSize) == 0:
        print("Warning: File contains no integer number of traces!")
    return int(fileSize / traceSize)