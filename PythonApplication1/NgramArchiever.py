import re
import os
from bitstring import BitArray


def encodeTextFile(filePath, outputFilePath = '/'):
	if outputFilePath == '/':
	    outputFilePath = os.path.splitext(filePath)[0] + '.nga'

	bfile = open(outputFilePath, "wb")

	textFile = open(filePath, "r", encoding="utf8")
	textFileLines = textFile.readlines()

	nLines = []
	shiftOut = False
	SO = chr(0x000E)
	SI = chr(0x000F)
	dict = getNgramDict()
	for line in textFileLines:
		words = line.split()
		nWords = []
		for word in words:
			if word.endswith((',', '.')):
				nWords.append(word[0:-1])
				nWords.append(word[-1:])
				#nWords.append(' ')
			else:
				nWords.append(word)
				#nWords.append(' ')
		#nWords.append('\n')

		#words = [str(dict[word]) if word in dict else word for word in nWords]
		words = []
		#if(nWords and nWords[0] in dict):
		#	words.append(SO); #SO
		#	shiftOut = True
		#else:
		#	shiftOut = False

		for word in nWords:
			if (word in dict) and not shiftOut:
				words.append(SO) #append SO and dict value
				words.append(dict[word]) 
				shiftOut = True
			elif (word in dict) and shiftOut:
				words.append(dict[word]) #just append dict value

			elif (word not in dict) and shiftOut:
				words.append(SI) #add SI to word and append
				words.append(word) 
				shiftOut = False
			elif (word not in dict) and not shiftOut:
				words.append(word) #just append word


		byteWriter = False #write unicode(default)
		bitStream = ''
		for word in words:
			if word == SO:
				byteWriter = True #activate byte writer
				bitStream = ''
				#write SO
				bfile.write(word.encode())
				continue
			elif word == SI:
				byteWriter = False #activate utf-8 writer	
				#TODO: split bitStream to bytes and write bytes
				bytesToWrite = convertBitsToBytes(bitStream)

				#write bytes
				bfile.write(bytesToWrite)
				#write SI
				bfile.write(word.encode())
				continue
			
			if not byteWriter:
				#write utf-8 word + ' '
				#if word in [',', '.']:
				#    bfile.write('\b'.encode())
				bfile.write(word.encode())#TODO: SPACE CHARACTER CHECK! (word + ' ')
			else:
				binNum = str(bin(word))[2:] #word to bin
				numLen = len(binNum)
				lenBits = ''
				if numLen < 14:
					bitsCount = len(str(bin(numLen))[2:]) #length of number length in bits 
					# This is the first 4 bits to identify number length (0001 - 1110)
					lenBits = '0' * (4 - bitsCount)
					lenBits += str(bin(numLen))[2:]
				else: 
					#If length is more than 14 than first 4 bits is 1111
					# and length of number will always be 18 bits(136000)
					binNum = ('0' * (18 - numLen)) + binNum
					lenBits = '1111'

				bitStream += lenBits
				bitStream += binNum
	print("File was compressed.")

def decodeTextFile(filePath, outputFilePath = '/'):
	if outputFilePath == '/':
	    outputFilePath = os.path.splitext(filePath)[0] + '.txt'

	bfileReader = open(filePath, "rb")

	dict = getNgramDict()

	SO = chr(0x000E)
	SI = chr(0x000F)


	fileBytes = bfileReader.read()

	bitsReader = False
	charStream = b''
	binStream = ''
	decoded = ''
	bits = ''
	bitsLeft = 0
	for b in fileBytes:
		byte = b.to_bytes(1, 'big')

		if bitsReader:
			bits += BitArray(byte).bin
			if bitsLeft == 0:
				if bits[0:4] == '0000':
					bits = ''
					bitsReader = False

	#					bits += '0000'
	#nullsToByte = 0 if (len(bits) % 8) == 0 else 8 - (len(bits) % 8)
	#bits += '0' * nullsToByte
	#bytesCount = len(bits) // 8
					#t = len(binStream) + 4
					#continue
				else:
					size = int(bits[0:4], 2)
					binStream += bits[0:4]
					bits = bits[4:]
					bitsLeft = size if size < 14 else 18
			else:
				#if bitsLeft == len(bits):
				#	binStream += bits
				#	bitsLeft = 0
				#	bits = ''
				if bitsLeft < len(bits):
					binStream += bits[0:bitsLeft]
					bits = bits[bitsLeft:]
					bitsLeft = 0
				else:
					binStream += bits
					bitsLeft -= len(bits)
					bits = ''

		if not bitsReader:
			char = chr(b)
			if char == SO:
				#if not charStream:
				decodedChars = charStream.decode(errors='ignore')
				print('c: ' + decodedChars)
				decoded += decodedChars
				bitsReader = True
				charStream = b''
				continue
			elif char == SI:
				decodedBits = decodeBinStream(binStream, dict)
				print('b: ' + decodedBits)
				decoded += decodedBits
				binStream = ''
				bitsReader = False
				continue
			else:
				charStream += byte

	decodedFile = open(outputFilePath, "w", encoding="utf-8")
	decodedFile.write(decoded)
	#print(decoded)
	print("File was decompressed.")


def decodeBinStream(binStream, dict):
	result = ''
	while len(binStream) > 0:
		if binStream[0:4] == '1111':
			size = 18
		else:
			size = int(binStream[0:4], 2)
		binStream = binStream[4:]
		num = binStream[0:size]
		binStream = binStream[size:]

		if len(num) == 0:
			return result
		value = int(num, 2)
		try:
			key = list(dict.keys())[list(dict.values()).index(value)]
			result += key 
		except:
			result += ''
			pass
	return result
	

def getNgramDict():
	file = open("C:/Users/danil/Downloads/ua_corpus/ua_google.txt", "r", encoding="utf8")
	lines = file.readlines()
	dict = {}
	i = 0
	for line in lines:
		line = line.strip()
		key = re.split(r'\t+', line)[1]
		dict[key] = i
		i += 1
	return dict

def convertBitsToBytes(bits):
	#End of stream
	bits += '0000'
	nullsToByte = 0 if (len(bits) % 8) == 0 else 8 - (len(bits) % 8)
	bits += '0' * nullsToByte
	bytesCount = len(bits) // 8
	return int(bits, 2).to_bytes(bytesCount, byteorder='big')
