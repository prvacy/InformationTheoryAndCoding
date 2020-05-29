import nltk
import re
from bitstring import BitArray


def compressTextFile():
	file = open("C:/Users/danil/Downloads/ua_corpus/ua_google.txt", "r", encoding="utf8")

	lines = file.readlines()

	dict = {}
	i = 0
	for line in lines:
		line = line.strip()
		key = re.split(r'\t+', line)[1]
		dict[key] = i
		i += 1


	news = open("C:/Users/danil/Downloads/ua_corpus/news1", "r", encoding="utf8")
	newsLines = news.readlines()

	nLines = []
	shiftOut = True
	for line in newsLines:
		words = line.split()
		nWords = []
		for word in words:
			if word.endswith((',', '.')):
				nWords.append(word[0:-1])
				nWords.append(word[-1:])
			else:
				nWords.append(word)

		#words = [str(dict[word]) if word in dict else word for word in nWords]
		words = []
		if(nWords and nWords[0] in dict):
			words.append(chr(0x000E)); #SO
		else:
			shiftOut = False

		for word in nWords:
			if word in dict and not shiftOut:
				words.append(chr(0x000E) + str(dict[word])) #append SO + dict value
				shiftOut = True
			elif word in dict and shiftOut:
				words.append(str(dict[word])) #just append dict value

			elif word not in dict and shiftOut:
				words.append(chr(0x000F) + word) #add SI to word and append
				shiftOut = False
			elif word not in dict and not shiftOut:
				words.append(word) #just append word


		nWords = []
		for cur, nxt in zip (words, words [1:] + ['end']):
			if(nxt in (',', '.')):
				nWords.append(cur + nxt)
			elif (cur in (',', '.')):	
				pass
			else:
				nWords.append(cur)

			#if(shiftOut and nxt not in dict):
			#	shiftOut = False
			#	nWords[-1] += chr(0x000F) #add Shift In to last word
			#elif(not shiftOut and nxt in dict):
			#	shiftOut = True
			#	nWords[-1] += chr(0x000E) #insert SO

		nLines.append(' '.join(nWords))
			
	for line in nLines:
		print(line)

def writeFile():
	bfile = open("C:/Users/danil/Downloads/ua_corpus/compressed", "wb")
	#bytes("україна", "utf8")

	file = open("C:/Users/danil/Downloads/ua_corpus/ua_google.txt", "r", encoding="utf8")

	lines = file.readlines()

	dict = {}
	i = 0
	for line in lines:
		line = line.strip()
		key = re.split(r'\t+', line)[1]
		dict[key] = i
		i += 1


	news = open("C:/Users/danil/Downloads/ua_corpus/news1", "r", encoding="utf8")
	newsLines = news.readlines()

	nLines = []
	shiftOut = True
	SO = chr(0x000E)
	SI = chr(0x000F)
	for line in newsLines:
		words = line.split()
		nWords = []
		for word in words:
			if word.endswith((',', '.')):
				nWords.append(word[0:-1])
				nWords.append(word[-1:])
				nWords.append(' ')
			else:
				nWords.append(word)
				nWords.append(' ')
		nWords.append('\n')

		#words = [str(dict[word]) if word in dict else word for word in nWords]
		words = []
		if(nWords and nWords[0] in dict):
			words.append(SO); #SO
		else:
			shiftOut = False

		for word in nWords:
			if word in dict and not shiftOut:
				words.append(SO) #append SO and dict value
				words.append(dict[word]) 
				shiftOut = True
			elif word in dict and shiftOut:
				words.append(dict[word]) #just append dict value

			elif word not in dict and shiftOut:
				words.append(SI) #add SI to word and append
				words.append(word) 
				shiftOut = False
			elif word not in dict and not shiftOut:
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


		#bfile.close()

def readFile(dict):
	SO = chr(0x000E)
	SI = chr(0x000F)
	bfileReader = open("C:/Users/danil/Downloads/ua_corpus/compressed", "rb")

	fileBytes = bfileReader.read()

	byteReader = False
	charStream = b''
	byteStream = b''
	decoded = ''
	for b in fileBytes:
		byte = b.to_bytes(1, 'big')
		char = chr(b)
		if char == SO:
			decoded += charStream.decode()
			byteReader = True
			charStream = b''
			continue
		elif char == SI:
			decodedBytes = decodeByteStream(byteStream, dict)
			decoded += decodedBytes
			byteStream = b''
			byteReader = False
			continue

		if not byteReader:
			charStream += byte
		else:
			byteStream += byte

	print(decoded)


def decodeByteStream(byteStream, dict):
	bits = BitArray(byteStream).bin
	result = ''
	while len(bits) > 0:
		if bits[0:4] == '1111':
			size = 18
		else:
			size = int(bits[0:4], 2)
		bits = bits[4:]
		num = bits[0:size]
		bits = bits[size:]

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
	



def convertBitsToBytes(bits):
	nullsToByte = 8 - len(bits) % 8
	bits += '0' * nullsToByte
	return int(bits, 2).to_bytes(len(bits) // 8, byteorder='big')


#compressTextFile()
writeFile()
file = open("C:/Users/danil/Downloads/ua_corpus/ua_google.txt", "r", encoding="utf8")

lines = file.readlines()

dict = {}
i = 0
for line in lines:
	line = line.strip()
	key = re.split(r'\t+', line)[1]
	dict[key] = i
	i += 1
readFile(dict)
