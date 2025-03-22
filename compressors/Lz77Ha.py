from collections import defaultdict
import heapq
def lz77_encode(data, buffer_size):
    encoded_data = bytearray()
    i = 0
    n = len(data)
    hash_table = defaultdict(list)
    
    while i < n:
        search_start = max(0, i - buffer_size)
        search_end = i
        search_window = data[search_start:i]
        max_length = 0
        max_offset = 0
        next_char = data[i] if i < n else b''
        current_hash = hash(data[i:i + 1])
        if current_hash in hash_table:
            for pos in hash_table[current_hash]:
                if pos < search_start:
                    continue
                length = 0
                while (i + length < n and pos + length < i and
                       data[i + length] == data[pos + length]):
                    length += 1
                if length > max_length:
                    max_length = length
                    max_offset = i - pos
                    next_char = data[i + length] if i + length < n else b''
        hash_table[current_hash].append(i)
        
        encoded_data.extend(max_offset.to_bytes(2, byteorder='big'))
        encoded_data.extend(max_length.to_bytes(2, byteorder='big'))
        encoded_data.append(next_char if next_char != b'' else 0)
        i += max_length + 1 if max_length > 0 else 1
    
    return bytes(encoded_data)

def lz77_decode(encoded_data, buffer_size):
    decoded_data = bytearray()
    i = 0
    n = len(encoded_data)
    
    while i < n:
        offset = int.from_bytes(encoded_data[i:i + 2], byteorder='big')
        length = int.from_bytes(encoded_data[i + 2:i + 4], byteorder='big')
        next_char = encoded_data[i + 4]
        
        if offset > 0 and length > 0:
            start = len(decoded_data) - offset
            end = start + length
            decoded_data.extend(decoded_data[start:end])
        if next_char != 0:
            decoded_data.append(next_char)
        i += 5
    
    return bytes(decoded_data)

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

def process_file(filename, block_size=1024, buffer_size=1024):
    with open(filename, 'rb') as f:
        data = f.read()
    blocks = [data[i:i+block_size] for i in range(0, len(data), block_size)]
    encoded_blocks = []
    block_lengths = [] 
    for block in blocks:
        lz77_encoded = lz77_encode(block, buffer_size)
        encoded_blocks.append(lz77_encoded)
        block_lengths.append(len(lz77_encoded)) 
    print('0')
    combined_data = b''.join(encoded_blocks)
    encoded_bytes, codebook, padding = encode_huffman(combined_data)
    print('1')
    compressed_filename = 'HelpPane_lz77ha_enc.exe'
    with open(compressed_filename, 'wb') as f:
        f.write(len(blocks).to_bytes(4, byteorder='big'))
        for length in block_lengths:
            f.write(length.to_bytes(4, byteorder='big'))
        write_compressed_file(f, encoded_bytes, codebook, padding)
    print(f"Файл '{filename}' успешно сжат. Результат записан в '{compressed_filename}'.")

    with open(compressed_filename, 'rb') as f:
        num_blocks = int.from_bytes(f.read(4), byteorder='big')
        block_lengths_read = [int.from_bytes(f.read(4), byteorder='big') for _ in range(num_blocks)]
        encoded_bytes_read, codebook_read, padding_read = read_compressed_file(f)
    
    decoded_data = decode_huffman(encoded_bytes_read, codebook_read, padding_read)
    print('2')
    decoded_blocks = []
    start = 0
    for length in block_lengths_read:
        end = start + length
        decoded_blocks.append(decoded_data[start:end])
        start = end
    print('3')
    original_blocks = []
    for block in decoded_blocks:
        lz77_decoded = lz77_decode(block, buffer_size)
        original_blocks.append(lz77_decoded)
    original_data = b''.join(original_blocks)
    print('4')
    decompressed_filename = 'HelpPane_lz77ha_dec.exe'
    with open(decompressed_filename, 'wb') as f:
        f.write(original_data)
    print(f"Файл '{compressed_filename}' успешно декомпрессирован. Результат записан в '{decompressed_filename}'.")
    with open(filename, 'rb') as f_original, open(decompressed_filename, 'rb') as f_decompressed:
        original = f_original.read()
        decompressed = f_decompressed.read()
        if original == decompressed:
            print("Декомпрессия успешна: исходные и декомпрессированные данные совпадают.")
        else:
            print("Ошибка: исходные и декомпрессированные данные не совпадают.")
#'gray_lz77ha_dec.raw''gray_lz77ha_enc.raw'
block_size = 64*1024
buffer_size = 64*1024
process_file('HelpPane.exe', block_size, buffer_size)