from NgramArchiever import encodeTextFile, decodeTextFile
import re

encodeTextFile("C:/Users/danil/Downloads/ua_corpus/news2.txt",
              "C:/Users/danil/Downloads/ua_corpus/news2.nga")

decodeTextFile("C:/Users/danil/Downloads/ua_corpus/news2.nga",
              "C:/Users/danil/Downloads/ua_corpus/news2_d.txt")
