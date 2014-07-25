import zlib
import base64
import argparse
import re
import sys

parser = argparse.ArgumentParser()
parser.add_argument("-t","--inputtext", help="operates directly on pasted code; may give a shell error with '!custom'; use a file instead")
parser.add_argument("-o","--outputfile", help="specify an output file")
parser.add_argument("-i","--inputfile", help="specify an input file with codes (1 per line)")
# nargs = 0
parser.add_argument("-d","--decompress", action="store_true", help="decompress and inflate only")
args = parser.parse_args()

# http://stackoverflow.com/questions/1089662/python-inflate-and-deflate-implementations
def decode_base64_and_inflate_string(b64string):
    decoded_data = base64.b64decode(b64string)
    return zlib.decompress(decoded_data, -15)

def decode_base64_and_inflate_list(i):
    return [decode_base64_and_inflate_string(j) for j in i]

def deflate_and_base64_encode_string(string_val):
    zlibbed_str = zlib.compress(string_val)
    compressed_string = zlibbed_str[2:-4]
    return base64.b64encode(compressed_string)

def deflate_and_base64_encode_list(i):
    return [deflate_and_base64_encode_string(j) for j in i]

def remove_code_name_and_indicator(code_list):
    saved_names = [re.sub(r'~#-.*$', '', code) for code in code_list]
    code_list = [re.sub(r'^(!custom)?.*~#-', '', code) for code in code_list]
    code_list = [re.sub(r'~$', '', code) for code in code_list]
    return (code_list, saved_names)

def add_back_name_and_indicator(unnamed_codes, saved_names):
    unnamed_codes = [code.decode('utf-8') for code in unnamed_codes]
    named_codes = [name + '~#-' + code + '~' for code, name in zip(unnamed_codes, saved_names)]
    return named_codes

def get_codes():
    # if and with don't define a scope
    if args.inputtext and args.inputfile:
        parser.print_help()
        sys.exit()
    elif args.inputtext:
        clc_list = [args.inputtext]
        return clc_list
    elif args.inputfile:
        with open (args.inputfile, "r") as somefile:
            clc_list = [line.rstrip('\n') for line in somefile]
            clc_list = [code for code in clc_list if code != '']
        return clc_list
    else:
        parser.print_help()
        sys.exit()

def return_codes():
    just_code, code_names = remove_code_name_and_indicator(get_codes())
    uncompressed = decode_base64_and_inflate_list(just_code)
    recompressed = deflate_and_base64_encode_list(uncompressed)
    final_codes = add_back_name_and_indicator(recompressed, code_names)
    if args.decompress and args.outputfile:
        with open (args.outputfile, "w") as outfile:
            for bin_data in uncompressed:
                bin_data = str(bin_data)[1:]
                if bin_data.startswith("'") and bin_data.endswith("'"):
                    bin_data = bin_data[1:-1]
                print(bin_data, '\n', file=outfile)
        sys.exit()
    elif args.decompress:
        for bin_data in uncompressed:
            bin_data = str(bin_data)[1:]
            if bin_data.startswith("'") and bin_data.endswith("'"):
                bin_data = bin_data[1:-1]
            print(bin_data, '\n')
        sys.exit()
    elif args.outputfile:
        with open (args.outputfile, "w") as outfile:
            for code in final_codes:
                print(code + '\n', file=outfile)
    else:
        for code in final_codes:
            print(code + '\n')

if __name__ == "__main__":
   return_codes()
