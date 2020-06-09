import re
import os
from bitstring import BitArray


def encodeTextFile(filePath, outputFilePath='/'):
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
				#words.append(' ')
				words.append(SO) #append SO and dict value
				words.append(dict[word]) 
				shiftOut = True
			elif (word in dict) and shiftOut:
				words.append(dict[word]) #just append dict value

			elif (word not in dict) and shiftOut:
				words.append(SI) #add SI to word and append
				words.append(word + ' ') 
				shiftOut = False
			elif (word not in dict) and not shiftOut:
				words.append(word + ' ') #just append word
				if word in [',', '.']:
					words[-2] = words[-2][0:-1]


		#if end of line and still shiftOut
		if shiftOut:
			words.append(SI)
			shiftOut = False


		words.append('\n')



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
				bfile.write(word.encode())#TODO: SPACE CHARACTER CHECK!  (word + ' ')
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

def decodeTextFile(filePath, outputFilePath='/'):
	if outputFilePath == '/':
	    outputFilePath = os.path.splitext(filePath)[0] + '.txt'

	bfileReader = open(filePath, "rb")

	dict = getNgramDict()

	SO = chr(0x000E)
	SI = chr(0x000F)


	fileBytes = bfileReader.read()
	fileBits = BitArray(fileBytes).bin

	bitsReader = False
	charStream = ''
	binStream = ''
	decoded = ''
	while len(fileBits) > 0:
		t = len(fileBits)
		#byte = fileBits[:4]
		#fileBits = fileBits[4:]

		if bitsReader:
			firstBits = fileBits[:4]
			fileBits = fileBits[4:]
			if firstBits == '0000':
				bStreamLen = len(binStream) + 4
				skip = 0 if bStreamLen % 8 == 0 else 8 - (bStreamLen % 8)
				fileBits = fileBits[skip:]
				bitsReader = False
			else:				
				size = 18 if firstBits == '1111' else int(firstBits, 2)
				binStream += firstBits + fileBits[:size]
				fileBits = fileBits[size:]
		else:
			char = chr(int(fileBits[:8], 2))
			bin = fileBits[:8]
			fileBits = fileBits[8:]

			if char == SO:
				charStreamHex = BitArray(bin=charStream).bytes
				decodedChars = charStreamHex.decode(errors='strict')
				#print('c: ' + decodedChars)
				#TODO: implement logger
				decoded += decodedChars
				bitsReader = True
				charStream = ''
				continue
			elif char == SI:
				decodedBits = decodeBinStream(binStream, dict)
				#print('b: ' + decodedBits)
				#TODO: implement logger
				decoded += decodedBits
				binStream = ''
				bitsReader = False
				
				nextChar = chr(int(fileBits[:8], 2))
				if nextChar in [',', '.']:
					decoded = decoded[:-1]
				continue
			else:
				charStream += bin

	if len(charStream) > 0:
		charStreamHex = BitArray(bin=charStream).bytes
		decodedChars = charStreamHex.decode(errors='strict')
		#print('c: ' + decodedChars)
		#TODO: implement logger
		decoded += decodedChars

	decoded = ''.join([line.rstrip() + '\n' for line in decoded.splitlines()])
	decoded = decoded[:-1]#delete newline
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
			result += ' '
		except:
			result += ''
			pass
	return result
	

def getNgramDict():
	file = open("./dict.txt", "r", encoding="utf8")
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
