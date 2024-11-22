""" TraceData class
 Methods to open and save D15 Trace Data meta and data files 
"""

import os, io
import sys
from shutil import copy2
import datetime
import hashlib
import configparser as configParser
import numpy as np
import align.tracelib.helperFunctions as helper

# TraceData library version
VERSION = "0.2"


class MetaObject(configParser.ConfigParser, object):
    def __init__(self, fileName=None):
        super(MetaObject, self).__init__()
        self.optionxform = lambda option: option
        self._okPlain = False
        self._okCipher = False
        self._okKey = False
        self.isLegacy = False

        if not fileName == None:
            self.load(fileName)

    def new(
        self,
        fileName,
        traceCount,
        randomPlain=True,
        randomKey=False,
        algorithm="aes128 ECB",
        needPlain=True,
        needCipher=True,
        needKey=True,
    ):
        if not needPlain:
            self._okPlain = True
        if not needCipher:
            self._okCipher = True
        if not needKey:
            self._okKey = True

        self.add_section("COMMON")
        self.set("COMMON", "nrTraces", str(traceCount))
        self.set("COMMON", "randomPlain", str(randomPlain))
        self.set("COMMON", "randomKey", str(randomKey))
        self.set("COMMON", "algorithm", str(algorithm))
        self.set("COMMON", "scopeSettings", "None")
        self.set("COMMON", "dateStart", str(datetime.datetime.now()))
        self.set("COMMON", "dateEnd", "")
        self.set("COMMON", "status", "incomplete")
        self.set("COMMON", "version", VERSION)
        self.set("COMMON", "recordScript", "")
        self.set("COMMON", "comment", "")

        self._setFileName(fileName)
        self._handleRecordScript()

    def _getScriptFilename(self):
        fileName = None
        try:
            import __main__ as evokeScript

            fileName = evokeScript.__file__
        except:
            print("Can't catch evoking script filename")
        return fileName

    def _copyRecordScript(self, fileName):
        baseName = os.path.basename(fileName)
        if os.path.isfile(self.path + baseName):
            suffix = 1
            while os.path.exists("{}_{}".format(self.path + baseName, suffix)):
                suffix += 1
            baseName = "{}_{}".format(baseName, suffix)
        copy2(fileName, self.path + baseName)
        return baseName

    def _setFileName(self, fileName):
        if fileName.endswith(".dat"):
            self.fileName = fileName[:-4] + ".meta"
        elif fileName.endswith(".meta"):
            self.fileName = fileName
        else:
            self.fileName = fileName + ".meta"
        self.fileName = os.path.abspath(fileName)
        self.path = os.path.dirname(self.fileName) + "/"

    def _handleRecordScript(self):
        fileName = self._getScriptFilename()
        baseName = ""
        if not fileName is None:
            baseName = self._copyRecordScript(fileName)
            self.set("COMMON", "recordScript", baseName)

    def writeMetaFile(self):
        with open(self.fileName, "w") as configFile:
            self.write(configFile, space_around_delimiters=True)

    def save(self):
        self.writeMetaFile()

    def load(self, fileName, fileStream=False):
        if not fileStream:
            if not os.path.isfile(fileName):
                print("MetaObject: Can't read meta information. File not found.")
                return

            try:
                self.read(fileName)
            # For older meta files without section headers -> one meta file for each data file
            except configParser.MissingSectionHeaderError:
                with open(fileName, "r") as inFile:
                    configString = "[DATA]\n" + inFile.read()
                    self.read_string(configString)
            self._setFileName(fileName)
        else:
            self.read_file(fileName)

        if self.has_section("DATA"):
            self.isLegacy = True
        if self.has_section("KEY"):
            self._okKey = True
        if self.has_section("PLAINTEXT"):
            self._okPlain = True
        if self.has_section("CIPHERTEXT"):
            self._okCipher = True

    def copy(self, fileName):
        newMetaObject = MetaObject()
        configString = io.StringIO()

        self.write(configString)
        configString.seek(0)
        newMetaObject.load(configString, fileStream=True)
        newMetaObject._setFileName(fileName)
        return newMetaObject

    def addComment(self, comment):
        newLine = "\n" if (len(self.get("COMMON", "comment")) > 0) else ""
        self.set(
            "COMMON", "comment", self.get("COMMON", "comment") + newLine + str(comment)
        )

    def complete(self, inputDir=None):
        self._checkSanity(inputDir=inputDir)
        self._computeFastHashs()
        self.set("COMMON", "dateEnd", str(datetime.datetime.now()))
        self.set("COMMON", "status", "complete")
        self.writeMetaFile()

    def _addDataSection(self, name, dtype, length, type="fixed"):
        if not self.has_section(name):
            self.add_section(name)
        self.set(name, "dtype", str(np.dtype(dtype)))
        self.set(name, "length", str(length))
        self.set(name, "type", type)
        if type == "file":
            self.set(name, "order", "row-major [trace, sample]")
            self.set(name, "datafile", "")
            self.set(name, "sha256", "")
            self.set(name, "fasthash", "")

    def _removeDataSection(self, name):
        if self.has_section(name):
            self.remove_section(name)

    def addFixedKey(self, key, dtype=np.uint8, length=16):
        self._addDataSection("KEY", dtype, length, "fixed")
        self.set("COMMON", "randomKey", "False")
        self.set("KEY", "data", bytearray(key).hex())
        self._okKey = True

    def addKeyFile(self, fileName, dtype=np.uint8, length=16):
        self._addDataSection("KEY", dtype, length, "file")
        self.set("KEY", "datafile", os.path.basename(fileName))
        self._okKey = True

    def removeKeyFile(self):
        self._removeDataSection("KEY")

    def setKeyHash(self, hash):
        self.setHash("KEY", hash)

    def addFixedPlain(self, plain, dtype=np.uint8, length=16):
        self._addDataSection("PLAINTEXT", dtype, length, "fixed")
        self.set("COMMON", "randomPlain", "False")
        self.set("PLAINTEXT", "data", bytearray(plain).hex())
        self._okPlain = True

    def addPlainFile(self, fileName, dtype=np.uint8, length=16):
        self._addDataSection("PLAINTEXT", dtype, length, "file")
        self.set("PLAINTEXT", "datafile", os.path.basename(fileName))
        self._okPlain = True

    def removePlainFile(self):
        self._removeDataSection("PLAINTEXT")

    def setPlainHash(self, hash):
        self.setHash("PLAINTEXT", hash)

    def addFixedCipher(self, cipher, dtype=np.uint8, length=16):
        self._addDataSection("CIPHERTEXT", dtype, length, "fixed")
        self.set("COMMON", "randomCipher", "False")
        self.set("CIPHERTEXT", "data", bytearray(cipher).hex())
        self._okCipher = True

    def addCipherFile(self, fileName, dtype=np.uint8, length=16):
        self._addDataSection("CIPHERTEXT", dtype, length, "file")
        self.set("CIPHERTEXT", "datafile", os.path.basename(fileName))
        self._okCipher = True

    def removeCipherFile(self):
        self._removeDataSection("CIPHERTEXT")

    def setCipherHash(self, hash):
        self.setHash("CIPHERTEXT", hash)

    def addPowerFile(self, fileName, dtype=np.uint8, length=16):
        self._addDataSection("POWER", dtype, length, "file")
        self.set("POWER", "datafile", os.path.basename(fileName))

    def removePowerFile(self):
        self._removeDataSection("POWER")
        self._removeDataSection("POWER_SCOPE")

    def setPowerHash(self, hash):
        self.setHash("POWER", hash)

    def addEMFile(self, fileName, dtype=np.uint8, length=16):
        self._addDataSection("EM", dtype, length, "file")
        self.set("EM", "datafile", os.path.basename(fileName))

    def removeEMFile(self):
        self._removeDataSection("EM")
        self._removeDataSection("EM_SCOPE")

    def setEMHash(self, hash):
        self.setHash("EM", hash)

    def addAuxFile(self, fileName, auxName, dtype=np.uint8, length=16):
        self._addDataSection("AUX{}".format(auxName), dtype, length, "file")
        self.set("AUX{}".format(auxName), "datafile", os.path.basename(fileName))

    def removeAuxFile(self, auxName):
        self._removeDataSection("AUX{}".format(auxName))

    def setAuxHash(self, auxName, hash):
        self.setHash("AUX{}".format(auxName), hash)

    def setHash(self, section, hash):
        self.set(section, "sha256", hash)

    def getAuxSections(self):
        return [x for x in self.sections() if x.startswith("AUX")]

    def getVersion(self):
        if self.has_option("COMMON", "version"):
            return self.get("COMMON", "version")
        else:
            return "legacy"

    def getStatus(self):
        if self.has_option("COMMON", "status"):
            return self.get("COMMON", "status")
        else:
            return "legacy"

    def getAlgorithm(self):
        if self.has_option("COMMON", "algorithm"):
            return self.get("COMMON", "algorithm")
        else:
            return None

    def isComplete(self):
        if self.getStatus() == "complete" or self.getStatus() == "legacy":
            return True
        else:
            return False

    def _computeFastHash(self, section):
        if self.has_section(section):
            if self.has_option(section, "type") and self.get(section, "type") == "file":
                if self.has_option(section, "fasthash") and self.get(
                    section, "fasthash"
                ):
                    if not self.get(section, "fasthash") == helper.fastHash(
                        self.path + self.get(section, "datafile")
                    ):
                        print(
                            "Warning - MetaObject: Fast hash of {} file seems corrupted! Old file not removed or overwritten?".format(
                                section
                            )
                        )
                self.set(
                    section,
                    "fasthash",
                    helper.fastHash(
                        os.path.dirname(self.fileName)
                        + "/"
                        + self.get(section, "datafile")
                    ),
                )

    def _computeFastHashs(self):
        for iSection in self.sections():
            self._computeFastHash(iSection)

    def _checkFileSize(self, section):
        return helper.checkFileSize(
            fileName=self.path + self.get(section, "datafile"),
            nrTraces=int(self.get("COMMON", "nrTraces")),
            length=int(self.get(section, "length")),
            dtype=np.dtype(self.get(section, "dtype")),
        )

    def _checkSanitySection(self, section, inputDir=None):
        if self.has_section(section):
            if self.has_option(section, "type") and self.get(section, "type") == "file":
                if not os.path.isfile(self.path + self.get(section, "datafile")):
                    if not inputDir is None:
                        if os.path.isfile(inputDir + self.get(section, "datafile")):
                            try:
                                copy2(
                                    inputDir + self.get(section, "datafile"), self.path
                                )
                                if not self._checkFileSize(section):
                                    print(
                                        "Warning - MetaObject: Copied {} file has incorrect size!".format(
                                            section
                                        )
                                    )
                            except:
                                print(
                                    "Warning - MetaObject: Failed copying {} file from source directory!".format(
                                        section
                                    )
                                )
                        else:
                            print(
                                "Warning - MetaObject: Can't locate {} file in source directory!".format(
                                    section
                                )
                            )
                    else:
                        print(
                            "Warning - MetaObject: Missing {} file in directory!".format(
                                section
                            )
                        )
                elif not self._checkFileSize(section):
                    print(
                        "Warning - MetaObject: {} file has incorrect size!".format(
                            section
                        )
                    )
                if self.get(section, "sha256") == "":
                    print("Warning - MetaObject: Missing {} file hash!".format(section))

    def _checkSanity(self, inputDir=None):
        ### Check if necessary data was registered
        if not self._okPlain:
            print("MetaObject: Missing plaintext!")

        if not self._okCipher:
            print("MetaObject: Missing ciphertext!")

        if not self._okKey:
            print("MetaObject: Missing key!")

        ### Check if all registered sections contain sane data
        for iSection in self.sections():
            self._checkSanitySection(iSection, inputDir=inputDir)

    def getNrTraces(self):
        if self.has_option("COMMON", "nrTraces"):
            return int(self.get("COMMON", "nrTraces"))
        elif self.has_option("DATA", "nr_traces"):
            return int(self.get("DATA", "nr_traces"))

    def setNrTraces(self, nrTraces):
        self.set("COMMON", "nrTraces", str(nrTraces))


class DataObject(object):
    def __init__(self, metaObject, section):
        self.metaObject = metaObject
        self.config = self.metaObject
        self.section = section
        self.data = None
        self.dtype = None  # data type for self.data, e.g. uint8, int8, int16 ...
        self.isFile = None
        self._recording = False

    def load(self):
        self.dtype = np.dtype(self.metaObject.get(self.section, "dtype"))
        self.length = int(self.metaObject.get(self.section, "length"))

        if self.metaObject.get(self.section, "type") == "file":
            self.fileName = self.metaObject.path + self.config.get(
                self.section, "datafile"
            )
            self.isFile = True
            if self.metaObject.isComplete():
                self.nrTraces = int(self.metaObject.get("COMMON", "nrTraces"))
                self.checkHash(fullCheck=False, verbose=False)
                spareBytes = helper.getSpareBytes(
                    self.fileName, self.nrTraces, self.length, self.dtype
                )
                self.length += spareBytes
                self.data = np.memmap(
                    self.fileName,
                    dtype=self.dtype,
                    mode="r",
                    shape=(self.nrTraces, self.length),
                )
            else:
                detectedTraces = helper.getMaximumTracesInFile(
                    self.fileName, self.length, self.dtype
                )
                print("WARNING - DataObject: Loading data with unknown status!")
                if not detectedTraces == self.metaObject.getNrTraces():
                    print(
                        "Try loading {} traces, expected {}".format(
                            detectedTraces, self.metaObject.getNrTraces()
                        )
                    )
                self.data = np.memmap(
                    self.fileName,
                    dtype=self.dtype,
                    mode="r",
                    shape=(detectedTraces, self.length),
                )
                if detectedTraces < self.metaObject.getNrTraces():
                    self.metaObject.setNrTraces(detectedTraces)
        else:
            self.isFile = False
            self.data = np.array(
                bytearray.fromhex(self.metaObject.get(self.section, "data")),
                dtype=self.dtype,
            )

    def checkHash(self, fullCheck=True, verbose=True):
        if not self.isFile:
            if verbose:
                print("DataObject: No file -> No hash")
            return
        try:
            if not fullCheck:
                if not helper.fastHash(self.fileName) == self.metaObject.get(
                    self.section, "fasthash"
                ):
                    print(
                        "WARNING - DataObject: Saved and computed hash (fast) are not matching!"
                    )
                elif verbose:
                    print("DataObject: Correct hash (fast)")
            else:
                if not helper.sha256Hash(self.fileName) == self.metaObject.get(
                    self.section, "sha256"
                ):
                    print(
                        "WARNING - DataObject: Saved and computed hash (full) are not matching!"
                    )
                elif verbose:
                    print("DataObject: Correct hash (sha256)")
        except:
            print(
                "WARNING - DataObject: Something crashed while checking hashes. Care?"
            )

    def _addTraceRaw(self, data):
        if not len(data) == (self.length * self.dtype.itemsize):
            print(
                "Warning - DataObject: Length mismatch! (Expected {}, got {})".format(
                    self.length * self.dtype.itemsize, len(data)
                )
            )
            return

        if self._saveMethod == "DIRECTWRITE":
            self.data.write(data)
        elif self._saveMethod == "MEMMAP":
            if self._recordsWritten >= self.nrTraces:
                print(
                    "Warning - DataObject: Can't write more traces into memmap! Ignoring trace."
                )
                return
            self.data[self._recordsWritten] = np.frombuffer(data, dtype=self.dtype)
        self._hasher.update(data)
        self._recordsWritten += 1

    def addTrace(self, data):
        if not self._recording:
            print("Error - DataObject: Not prepared for record, can't add trace!")
            return
        if isinstance(data, bytes) or isinstance(data, bytearray):
            self._addTraceRaw(data)
        elif isinstance(data, list):
            self._addTraceRaw(bytearray(data))
        elif isinstance(data, np.ndarray):
            self._addTraceRaw(data.tobytes())
        else:
            print(
                "Error - DataObject: Unsupported data format! Try bytearray, list or numpy.ndarray."
            )

    def prepareForRecord(
        self, fileName, nrTraces, length, dtype, saveMethod="DIRECTWRITE"
    ):
        self.isFile = True
        self._saveMethod = saveMethod
        self._recordsWritten = 0
        self._recording = True
        self._hasher = hashlib.sha256()

        self.nrTraces = int(nrTraces)
        self.length = int(length)
        self.dtype = np.dtype(dtype)

        if self._saveMethod == "DIRECTWRITE":
            self.data = open(fileName, "w+b")
        elif self._saveMethod == "MEMMAP":
            self.data = np.memmap(
                fileName, dtype=dtype, mode="w+", shape=(self.nrTraces, self.length)
            )

    def finishRecord(self):
        if not self._recording:
            print("Warning - DataObject: Can't finish what was never started!")
            return

        if self._saveMethod == "DIRECTWRITE":
            self.data.close()
        elif self._saveMethod == "MEMMAP":
            self.data.flush()

        self.metaObject.setHash(self.section, self._hasher.hexdigest())
        if not self._recordsWritten == self.metaObject.getNrTraces():
            print(
                "Warning - DataObject: Number of written records does not match nrTraces in config!"
            )

    def getSampleFrequency(self):
        if self.metaObject.has_option(self.section + "_SCOPE", "HORIZ_INTERVAL"):
            return (
                float(self.metaObject.get(self.section + "_SCOPE", "HORIZ_INTERVAL"))
                ** -1
            )

    def reduceFrom(self, inputData, traceMask):
        if not self._recording:
            print(
                "Error - DataObject.reduceFrom(): Not prepared for record, can't reduce set of traces!"
            )
            return

        if not (
            isinstance(inputData, DataObject) and isinstance(traceMask, np.ndarray)
        ):
            print("Error - DataObject.reduceFrom(): Invalid input types!")
            return

        if inputData.data.shape[0] < traceMask.shape[0]:
            print(
                "Error - DataObject.reduceFrom(): Length mismatch! Trace mask is larger than input set."
            )
            return

        if inputData.data.shape[0] > traceMask.shape[0]:
            print(
                "Warning - DataObject.reduceFrom(): Length mismatch! Trace mask is shorter than input set."
            )

        for iTrace in range(traceMask.shape[0]):
            if traceMask[iTrace]:
                self._addTraceRaw(inputData.data[iTrace].tobytes())


class TraceData(object):
    def __init__(self, fileName=None):
        self.config = MetaObject()
        self.hasKey = False
        self.hasPlain = False
        self.hasCipher = False
        self.hasEM = False
        self.hasPower = False
        self.hasAux = False
        self._recording = False

        ### inputDir is used in newFrom method
        self.inputDir = None

        if not fileName == None:
            if os.path.isfile(fileName):
                self.open(fileName)
            else:
                raise ValueError("File {} does not exist!".format(fileName))

    # Legacy method to work with old measurements and meta files that use old or none configParser scheme
    # With this, new TraceData Objects should work as a full, backwards compatible replacement in old scripts
    def _openLegacy(self):
        if not set(["dtype", "data", "nr_points", "nr_traces"]).issubset(
            self.config.options("DATA")
        ):
            print(
                "TraceData - open: Can't find all necessary data in legacy meta file!"
            )
            raise ValueError("No meta data")

        self.fileName = self.config.path + self.config.get("DATA", "data")
        self.dtype = np.dtype(self.config.get("DATA", "dtype"))
        self.nr_points = int(self.config.get("DATA", "nr_points"))
        self.nr_traces = int(self.config.get("DATA", "nr_traces"))

        # Check sizes for sanity
        spareBytes = 0
        fileSize = os.path.getsize(self.fileName)
        arraySize = self.dtype.itemsize * self.nr_traces * self.nr_points
        if not fileSize == (arraySize):
            print(
                "Warning: Size of {} ({}) and size of array ({} * {} * {} = {}) do not match!".format(
                    self.fileName,
                    fileSize,
                    self.dtype.itemsize,
                    self.nr_traces,
                    self.nr_points,
                    arraySize,
                )
            )
            if fileSize < arraySize:
                raise ValueError("Size mismatch! File size < array size")
            else:
                if ((fileSize - arraySize) % self.nr_traces) == 0:
                    spareBytes = int((fileSize - arraySize) / self.nr_traces)
                    print(
                        "Found exactly {} additional byte(s) per Trace (EOL char?).".format(
                            spareBytes
                        )
                    )
                    print("Adding them to # of sample points")

        self.data = np.memmap(
            self.fileName,
            dtype=self.dtype,
            mode="r",
            shape=(self.nr_traces, self.nr_points + spareBytes),
        )

        if self.config.has_option("DATA", "plaintext"):
            self.plain = np.memmap(
                self.config.path + self.config.get("DATA", "plaintext"),
                dtype=np.uint8,
                mode="r",
                shape=(self.nr_traces, 16),
            )
        if self.config.has_option("DATA", "ciphertext"):
            self.cipher = np.memmap(
                self.config.path + self.config.get("DATA", "ciphertext"),
                dtype=np.uint8,
                mode="r",
                shape=(self.nr_traces, 16),
            )
        if self.config.has_option("DATA", "key"):
            self.key = np.array(
                bytearray.fromhex(self.config.get("DATA", "key")), dtype=np.uint8
            )
        if self.config.has_option("DATA", "keys"):
            self.keys = np.memmap(
                self.config.path + self.config.get("DATA", "keys"),
                dtype=np.uint8,
                mode="r",
                shape=(self.nr_traces, 16),
            )

    def _loadKey(self):
        if not self.config.has_section("KEY"):
            return
        self.key = DataObject(self.config, "KEY")
        self.key.load()
        self.hasKey = True

    def _loadPlain(self):
        if not self.config.has_section("PLAINTEXT"):
            return
        self.plain = DataObject(self.config, "PLAINTEXT")
        self.plain.load()
        self.hasPlain = True

    def _loadCipher(self):
        if not self.config.has_section("CIPHERTEXT"):
            return
        self.cipher = DataObject(self.config, "CIPHERTEXT")
        self.cipher.load()
        self.hasCipher = True

    def _loadPower(self):
        if not self.config.has_section("POWER"):
            return
        self.power = DataObject(self.config, "POWER")
        self.power.load()
        self.hasPower = True

    def _loadEM(self):
        if not self.config.has_section("EM"):
            return
        self.em = DataObject(self.config, "EM")
        self.em.load()
        self.hasEM = True

    def _loadAux(self):
        for iAux in self.config.getAuxSections():
            if not self.hasAux:
                self.aux = {}
            self.aux[iAux[3:]] = DataObject(self.config, iAux)
            self.aux[iAux[3:]].load()
            self.hasAux = True

    def _checkVersion(self):
        if self.config.getVersion() == VERSION:
            return True
        elif (
            self.config.getVersion() > VERSION
            and not self.config.getVersion() == "legacy"
        ):
            print(
                "Warning - D15tools: Data was recorded using v{} (yours is v{}). Consider updating!".format(
                    self.config.getVersion(), VERSION
                )
            )
            return False
        else:
            print(
                "Warning - D15tools: Data was recorded using v{} (yours is v{}). Better hope for downward compatibility...".format(
                    self.config.getVersion(), VERSION
                )
            )
            return False

    def open(self, fileName):
        self.config.load(fileName)

        if self.config.isLegacy:
            self._openLegacy()
        else:
            self._checkVersion()
            self.nrTraces = self.config.getNrTraces()
            self._loadKey()
            self._loadPlain()
            self._loadCipher()
            self._loadPower()
            self._loadEM()
            self._loadAux()

    def startRecord(
        self,
        fileName,
        traceCount,
        randomPlain=True,
        randomKey=False,
        algorithm="aes128",
        needPlain=True,
        needCipher=True,
        needKey=True,
    ):
        helper.checkDir(os.path.dirname(os.path.abspath(fileName)))
        self._recording = True
        self.config.new(
            fileName=fileName,
            traceCount=traceCount,
            randomPlain=randomPlain,
            randomKey=randomKey,
            algorithm=algorithm,
            needPlain=needPlain,
            needCipher=needCipher,
            needKey=needKey,
        )
        self.nrTraces = int(traceCount)

    def newFrom(self, fileName, inputFile):
        helper.checkDir(os.path.dirname(os.path.abspath(fileName)))
        self.inputDir = (
            helper.checkDir(os.path.dirname(os.path.abspath(inputFile))) + "/"
        )
        self._recording = True
        oldConfig = MetaObject(inputFile)
        self.config = oldConfig.copy(fileName)
        self.config.addComment("Source file: {}".format(inputFile))
        self.config.set("COMMON", "status", "incomplete")
        self.config.set("COMMON", "version", VERSION)
        self.nrTraces = self.config.getNrTraces()

    def registerKeyFile(
        self, fileName, length=16, dtype=np.uint8, saveMethod="DIRECTWRITE"
    ):
        if not self._recording:
            print(
                "Warning - TraceData: Can't register file before new record was started!"
            )
            return
        self.config.addKeyFile(fileName, dtype=dtype, length=length)
        self.key = DataObject(self.config, "KEY")
        self.key.prepareForRecord(
            fileName=self.config.path + os.path.basename(fileName),
            saveMethod=saveMethod,
            nrTraces=self.nrTraces,
            length=length,
            dtype=dtype,
        )
        self.hasKey = True

    def registerPlainFile(
        self, fileName, length=16, dtype=np.uint8, saveMethod="DIRECTWRITE"
    ):
        if not self._recording:
            print(
                "Warning - TraceData: Can't register file before new record was started!"
            )
            return
        self.config.addPlainFile(fileName, dtype=dtype, length=length)
        self.plain = DataObject(self.config, "PLAINTEXT")
        self.plain.prepareForRecord(
            fileName=self.config.path + os.path.basename(fileName),
            saveMethod=saveMethod,
            nrTraces=self.nrTraces,
            length=length,
            dtype=dtype,
        )
        self.hasPlain = True

    def registerCipherFile(
        self, fileName, length=16, dtype=np.uint8, saveMethod="DIRECTWRITE"
    ):
        if not self._recording:
            print(
                "Warning - TraceData: Can't register file before new record was started!"
            )
            return
        self.config.addCipherFile(fileName, dtype=dtype, length=length)
        self.cipher = DataObject(self.config, "CIPHERTEXT")
        self.cipher.prepareForRecord(
            fileName=self.config.path + os.path.basename(fileName),
            saveMethod=saveMethod,
            nrTraces=self.nrTraces,
            length=length,
            dtype=dtype,
        )
        self.hasCipher = True

    def registerPowerFile(
        self, fileName, length, dtype=np.uint8, saveMethod="DIRECTWRITE"
    ):
        if not self._recording:
            print(
                "Warning - TraceData: Can't register file before new record was started!"
            )
            return
        self.config.addPowerFile(fileName, dtype=dtype, length=length)
        self.power = DataObject(self.config, "POWER")
        self.power.prepareForRecord(
            fileName=self.config.path + os.path.basename(fileName),
            saveMethod=saveMethod,
            nrTraces=self.nrTraces,
            length=length,
            dtype=dtype,
        )
        self.hasPower = True

    def registerEMFile(
        self, fileName, length, dtype=np.uint8, saveMethod="DIRECTWRITE"
    ):
        if not self._recording:
            print(
                "Warning - TraceData: Can't register file before new record was started!"
            )
            return
        self.config.addEMFile(fileName, dtype=dtype, length=length)
        self.em = DataObject(self.config, "EM")
        self.em.prepareForRecord(
            fileName=self.config.path + os.path.basename(fileName),
            saveMethod=saveMethod,
            nrTraces=self.nrTraces,
            length=length,
            dtype=dtype,
        )
        self.hasEM = True

    def registerAuxFile(
        self, fileName, auxName, length, dtype=np.uint8, saveMethod="DIRECTWRITE"
    ):
        if not self._recording:
            print(
                "Warning - TraceData: Can't register file before new record was started!"
            )
            return
        self.config.addAuxFile(fileName, auxName, dtype=dtype, length=length)
        if not self.hasAux:
            self.aux = {}
        self.aux[str(auxName)] = DataObject(self.config, "AUX{}".format(auxName))
        self.aux[str(auxName)].prepareForRecord(
            fileName=self.config.path + os.path.basename(fileName),
            saveMethod=saveMethod,
            nrTraces=self.nrTraces,
            length=length,
            dtype=dtype,
        )
        self.hasAux = True

    def unregisterKeyFile(self):
        self.config.removeKeyFile()

    def unregisterPlainFile(self):
        self.config.removePlainFile()

    def unregisterCipherFile(self):
        self.config.removeCipherFile()

    def unregisterPowerFile(self):
        self.config.removePowerFile()

    def unregisterEMFile(self):
        self.config.removeEMFile()

    def unregisterAuxFile(self, auxName):
        self.config.removeAuxFile(auxName)

    def finishRecord(self, copyMissing=True):
        if not self._recording:
            print("Warning - TraceData: Can't finish record before record was started!")
            return

        if self.hasKey:
            self.key.finishRecord()
        if self.hasPlain:
            self.plain.finishRecord()
        if self.hasCipher:
            self.cipher.finishRecord()
        if self.hasPower:
            self.power.finishRecord()
        if self.hasEM:
            self.em.finishRecord()
        if self.hasAux:
            for iAux in self.config.getAuxSections():
                self.aux[iAux[3:]].finishRecord()

        inputDir = self.inputDir if copyMissing else None
        self.config.complete(inputDir=inputDir)

    def getNrTraces(self):
        return self.config.getNrTraces()

    def setNrTraces(self, nrTraces):
        self.config.setNrTraces(nrTraces)
        self.nrTraces = nrTraces
