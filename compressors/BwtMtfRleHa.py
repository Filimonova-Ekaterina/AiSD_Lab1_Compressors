import heapq
def rle_encode(data,M):
    if not data:
        return b""
    encoded = bytearray()
    block_size =M//8
    count = 1
    repeat_flag=0
    prev_char = data[:block_size ]
    j=0
    data += b'\xFF' * block_size 
    i=block_size 
    while (i<len(data)):
        char=data[i:i+block_size ]
        if (char==prev_char and count<127):
            count+=1
            i+=block_size 
            repeat_flag=1
        else:
            if (repeat_flag==1):
                encoded.append(count)
                encoded.extend(prev_char)
                count=1
                repeat_flag=0
                prev_char=char
                i+=block_size 
            else:
                j=0
                dop_str=bytearray()
                while(char!=prev_char and j<127 and i+j*block_size <len(data)):
                    j+=1
                    dop_str.extend(prev_char)
                    prev_char=char
                    char=data[i+j*block_size :i+j*block_size +block_size ] if i+j*block_size <len(data) else b''
                encoded.append(j|0x80)
                encoded.extend(dop_str)
                i+=j*block_size 
    return bytes(encoded)

def rle_decode(data,M):
    if not data:
        return b""
    decoded = bytearray()
    i = 0
    block_size =M//8
    while i < len(data):
        count = (data[i])
        if (count & 0x80):
            length = count& 0x7F
            decoded.extend(data[i+1: i+1+length*block_size ])
            i+=1+length*block_size 
        else:
            char = data[i + 1:i+1+block_size]
            decoded.extend(char * count)
            i += 1+block_size 
    return bytes(decoded)

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    def __lt__(self, other):
        return self.freq < other.freq

def count_frequencies(data):
    freq_map = {}
    for char in data:
        if char in freq_map:
            freq_map[char] += 1
        else:
            freq_map[char] = 1
    return freq_map

def build_huffman_tree(freq_map):
    heap = [HuffmanNode(char, freq) for char, freq in freq_map.items()]
    heapq.heapify(heap)
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        merged = HuffmanNode(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heapq.heappush(heap, merged)
    return heap[0]

def build_codebook(root, code="", codebook=None):
    if codebook is None:
        codebook = {}
    if root:
        if root.char is not None:
            codebook[root.char] = code
        build_codebook(root.left, code + "0", codebook)
        build_codebook(root.right, code + "1", codebook)
    return codebook

def encode_huffman(data):
    freq_map = count_frequencies(data)
    root = build_huffman_tree(freq_map)
    codebook = build_codebook(root)
    encoded_bits = ''.join([codebook[char] for char in data])
    padding = 8 - len(encoded_bits) % 8
    encoded_bits += '0' * padding
    encoded_bytes = bytes([int(encoded_bits[i:i+8], 2) for i in range(0, len(encoded_bits), 8)])
    return encoded_bytes, codebook, padding

def decode_huffman(encoded_bytes, codebook, padding):
    encoded_bits = ''.join([f"{byte:08b}" for byte in encoded_bytes])
    encoded_bits = encoded_bits[:-padding] if padding > 0 else encoded_bits
    reverse_codebook = {v: k for k, v in codebook.items()}
    current_code = ""
    decoded_data = []
    for bit in encoded_bits:
        current_code += bit
        if current_code in reverse_codebook:
            decoded_data.append(reverse_codebook[current_code])
            current_code = ""
    return bytes(decoded_data)

def write_compressed_file(file_obj, encoded_bytes, codebook, padding):
    file_obj.write(bytes([padding]))
    codebook_size = len(codebook)
    file_obj.write(codebook_size.to_bytes(2, byteorder='big'))
    for char, code in codebook.items():
        file_obj.write(bytes([char]))
        code_length = len(code)
        file_obj.write(bytes([code_length]))
        padded_code = code + '0' * (8 - code_length % 8) if code_length % 8 != 0 else code
        code_bytes = int(padded_code, 2).to_bytes((len(padded_code) + 7) // 8, byteorder='big')
        file_obj.write(code_bytes)
    file_obj.write(encoded_bytes)

def read_compressed_file(file_obj):
    padding = int.from_bytes(file_obj.read(1), byteorder='big')
    codebook_size = int.from_bytes(file_obj.read(2), byteorder='big')
    codebook = {}
    for _ in range(codebook_size):
        char = int.from_bytes(file_obj.read(1), byteorder='big')
        code_length = int.from_bytes(file_obj.read(1), byteorder='big')
        code_bytes_length = (code_length + 7) // 8
        code_bytes = file_obj.read(code_bytes_length)
        code_bits = ''.join(f"{byte:08b}" for byte in code_bytes)
        code = code_bits[:code_length]
        codebook[char] = code
    encoded_bytes = file_obj.read()
    return encoded_bytes, codebook, padding

def mtf_encode(data):
    alphabet = list(range(256))
    result = bytearray()

    for byte in data:
        index = alphabet.index(byte)
        result.append(index)
        alphabet.pop(index)
        alphabet.insert(0, byte)

    return bytes(result)

def mtf_decode(data):
    alphabet = list(range(256))
    result = bytearray()

    for index in data:
        byte = alphabet[index]
        result.append(byte)
        alphabet.pop(index)
        alphabet.insert(0, byte)

    return bytes(result)

def counting_sort(last_column):
    count = [0] * 256
    for char in last_column:
        count[char] += 1

    for i in range(1, 256):
        count[i] += count[i - 1]

    P_inverse = [0] * len(last_column)
    for i in range(len(last_column) - 1, -1, -1):
        char = last_column[i]
        count[char] -= 1
        P_inverse[count[char]] = i

    return P_inverse

def build_suffix_array(s):
    n = len(s)
    suffixes = [(s[i:], i) for i in range(n)]
    suffixes.sort()
    suffix_array = [idx for _, idx in suffixes]
    return suffix_array

def bwt_encode(data):
    if not data:
        return b""
    marker = 0xFF
    data_with_marker = data + bytes([marker])
    n = len(data_with_marker)
    sa = build_suffix_array(data_with_marker)
    last_column = bytearray(data_with_marker[(sa[i] - 1) % n] for i in range(n))
    return bytes(last_column)

def bwt_decode(encoded_data):
    if not encoded_data:
        return b""
    marker = 0xFF
    S_index = encoded_data.find(marker)
    if S_index == -1:
        raise ValueError("Маркер конца данных не найден")
    last_column = list(encoded_data)
    P_inverse = counting_sort(last_column)
    N = len(last_column)
    S = bytearray()
    j = S_index
    for _ in range(N):
        j = P_inverse[j]
        S.append(last_column[j])
    return bytes(S).rstrip(bytes([marker]))


buffer_size = 1024
M = 8 #color = 24, gray = 8, bw = 8, enw = 16, kup=8, 1mb = 128
block_size = 1024

def process_file(filename, block_size=16*1024,M =8):
    with open(filename, 'rb') as f:
        data = f.read()
    blocks = [data[i:i+block_size] for i in range(0, len(data), block_size)]
    encoded_blocks = []
    block_lengths = [] 
    for block in blocks:
        bwt_encoded = bwt_encode(block)
        mtf_encoded = mtf_encode(bwt_encoded)
        rle_encoded = rle_encode(mtf_encoded,M)
        encoded_blocks.append(rle_encoded)
        block_lengths.append(len(rle_encoded)) 

    combined_data = b''.join(encoded_blocks)
    encoded_bytes, codebook, padding = encode_huffman(combined_data)
    compressed_filename = 'HelpPane_bmrh_enc.exe'
    with open(compressed_filename, 'wb') as f:
        f.write(len(blocks).to_bytes(4, byteorder='big'))
        for length in block_lengths:
            f.write(length.to_bytes(4, byteorder='big'))
        write_compressed_file(f, encoded_bytes, codebook, padding)

    with open(compressed_filename, 'rb') as f:
        num_blocks = int.from_bytes(f.read(4), byteorder='big')
        block_lengths_read = [int.from_bytes(f.read(4), byteorder='big') for _ in range(num_blocks)]
        encoded_bytes_read, codebook_read, padding_read = read_compressed_file(f)

    decoded_data = decode_huffman(encoded_bytes_read, codebook_read, padding_read)
    decoded_blocks = []
    start = 0
    for length in block_lengths_read:
        end = start + length
        decoded_blocks.append(decoded_data[start:end])
        start = end

    original_blocks = []
    for block in decoded_blocks:
        rle_decoded = rle_decode(block,M)
        mtf_decoded = mtf_decode(rle_decoded)
        bwt_decoded = bwt_decode(mtf_decoded)
        original_blocks.append(bwt_decoded)
    original_data = b''.join(original_blocks)
    decompressed_filename = 'HelpPane_bmrh_dec.exe'
    with open(decompressed_filename, 'wb') as f:
        f.write(original_data)

    print(f"Файл '{filename}' успешно обработан. Результат записан в '{compressed_filename}' и '{decompressed_filename}'.")
    with open(filename, 'rb') as f_out, open (decompressed_filename,'rb') as f_in:
        dec=f_out.read()
        init = f_in.read()
        if dec==init:
            print('победа')
        else:
            print('во блин')

process_file('HelpPane.exe')
