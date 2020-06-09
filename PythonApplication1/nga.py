from NgramArchiever import encodeTextFile, decodeTextFile
import argparse

parser = argparse.ArgumentParser(description='N-gram based text archiver.')

parser.add_argument('src', metavar='file', type=str, #nargs='1',
                   help='File path to compress')
parser.add_argument('-n', '-name', dest='dst', type=str, 
                   action='store',
                   default='/',
                   help='File path to compress')

parser.add_argument('-c', '-compress', dest='command', action='store_const',
                   const=encodeTextFile,
                   help='Compress file')
parser.add_argument('-d', '-decompress', dest='command', action='store_const',
                   const=decodeTextFile,
                   help='Decompress file')



args = parser.parse_args()
args.command(args.src, args.dst)

#encodeTextFile("C:/Users/danil/Downloads/ua_corpus/news1.txt",
#              "C:/Users/danil/Downloads/ua_corpus/news1.nga")

#decodeTextFile("C:/Users/danil/Downloads/ua_corpus/news1.nga",
#              "C:/Users/danil/Downloads/ua_corpus/news1_d.txt")
