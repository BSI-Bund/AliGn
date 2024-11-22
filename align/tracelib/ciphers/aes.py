import numba as nb
import numpy as np
from align.tracelib.ciphers.aesConstants import SBox32, Te0, Te1, Te2, Te3, Rcon32


# KEY EXPANSION

@nb.njit("u4(u4[:],u1)")
def scheduleCore32(word, i):
    word[0] = word[0]<<8 | word[0]>>24
    word[0] = (SBox32[word[0]>>24])<<24 | (SBox32[word[0]>>16 & 0xff])<<16 |    (SBox32[word[0]>>8&0xff])<<8 |(SBox32[word[0]&0xff])
    word[0] = word[0] ^ (Rcon32[i] << 24)
    return word[0]

@nb.njit("u4[:](u4[:])")
def expandKey32(key):
    tmp = np.zeros(1, dtype = np.uint32)
    fullKey = np.zeros(44, dtype = np.uint32)
    fullKey[:4] = key
    iWord = 4
    iRound = 1
    while iWord < 44:
        tmp[0] = fullKey[iWord-1]
        if (iWord % 4) == 0:
            tmp[0] = scheduleCore32(tmp, iRound)
            iRound += 1
        fullKey[iWord] = fullKey[iWord-4] ^ tmp[0]
        iWord += 1
    return fullKey

# AES OPERATION

@nb.njit("u4[:](u4[:])")
def subShift32(block):
    tmp = np.zeros(4, dtype = np.uint32)
    tmp[0] = (SBox32[block[0]>>24])<<24 | (SBox32[block[1]>>16 & 0xff])<<16 |    (SBox32[block[2]>>8&0xff])<<8 |(SBox32[block[3]&0xff])
    tmp[1] = (SBox32[block[1]>>24])<<24 | (SBox32[block[2]>>16 & 0xff])<<16 |    (SBox32[block[3]>>8&0xff])<<8 |(SBox32[block[0]&0xff])
    tmp[2] = (SBox32[block[2]>>24])<<24 | (SBox32[block[3]>>16 & 0xff])<<16 |    (SBox32[block[0]>>8&0xff])<<8 |(SBox32[block[1]&0xff])
    tmp[3] = (SBox32[block[3]>>24])<<24 | (SBox32[block[0]>>16 & 0xff])<<16 |    (SBox32[block[1]>>8&0xff])<<8 |(SBox32[block[2]&0xff])
    return tmp

@nb.njit("u4[:](u4[:])")
def roundLookup32(block):
    tmp = np.zeros(4, dtype = np.uint32)
    tmp[0] = Te0[block[0]>>24] ^ Te1[block[1] >> 16 & 0xff] ^ Te2[block[2] >> 8 & 0xff] ^ Te3[block[3] & 0xff]
    tmp[1] = Te0[block[1]>>24] ^ Te1[block[2] >> 16 & 0xff] ^ Te2[block[3] >> 8 & 0xff] ^ Te3[block[0] & 0xff]
    tmp[2] = Te0[block[2]>>24] ^ Te1[block[3] >> 16 & 0xff] ^ Te2[block[0] >> 8 & 0xff] ^ Te3[block[1] & 0xff]
    tmp[3] = Te0[block[3]>>24] ^ Te1[block[0] >> 16 & 0xff] ^ Te2[block[1] >> 8 & 0xff] ^ Te3[block[2] & 0xff]
    return tmp

@nb.njit("u4[:](u4[:],u4[:])")
def aesTL32(plain, expandedKey):
    state = np.zeros(4, dtype = np.uint32)
    #AddRoundKey
    state[:] = plain ^ expandedKey[:4]
    for iRound in range(1,10):
        state[:] = roundLookup32(state)
        state[:] = state ^ expandedKey[iRound*4:(iRound*4)+4]
    state[:] = subShift32(state)
    state[:] = state ^ expandedKey[40:]
    return state

np.set_printoptions(formatter={'int':hex})

### API

class AESEngine(object):
    def __init__(self):
        self.dt = np.dtype(np.uint32)
        self.dt = self.dt.newbyteorder('B')
        self.plaintext = np.zeros(4, dtype = np.uint32)
        self.ciphertext = np.zeros(4, dtype = np.uint32)
        self.key = np.zeros(4, dtype = np.uint32)
        self.expandedKey = np.zeros(44, dtype = np.uint32)
        
    def _transformInput(self, _input):
        input32 = np.frombuffer(_input, dtype = self.dt)
        return input32

    def setKey(self, key):
        self.key[:] = self._transformInput(key)
        self.expandedKey[:] = expandKey32(self.key)

    def encrypt(self, plaintext, returnType = np.uint32):
        self.plaintext[:] = self._transformInput(plaintext)
        self.ciphertext[:] = aesTL32(self.plaintext, self.expandedKey)
        if returnType is np.uint32:
            return self.ciphertext
        else:
            ciphertext = self.ciphertext.astype('>u4') # Change Byteorder if necessary
            return ciphertext.view(returnType)

### TESTS
if __name__ == "__main__":
	testKey = np.array([0x2b, 0x7e, 0x15, 0x16, 0x28, 0xae, 0xd2, 0xa6, 0xab, 0xf7, 0x15, 0x88, 0x09, 0xcf, 0x4f, 0x3c], dtype = np.uint8)
	testPlain = np.array([0x6b, 0xc1, 0xbe, 0xe2, 0x2e, 0x40, 0x9f, 0x96, 0xe9, 0x3d, 0x7e, 0x11, 0x73, 0x93, 0x17, 0x2a], dtype = np.uint8)

	print("Engine Test\n")

	Engine = AESEngine()
	Engine.setKey(testKey)
	cipher = Engine.encrypt(testPlain)
	print(cipher)
	cipher8 = Engine.encrypt(testPlain, returnType = np.uint8)
	print(cipher8)

