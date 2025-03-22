import heapq

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

def write_compressed_file(filename, encoded_bytes, codebook, padding):
    with open(filename, 'wb') as f:
        f.write(bytes([padding]))
        codebook_size = len(codebook)
        f.write(codebook_size.to_bytes(2, byteorder='big'))
        for char, code in codebook.items():
            f.write(bytes([char]))
            code_length = len(code)
            f.write(bytes([code_length]))
            padded_code = code + '0' * (8 - code_length % 8) if code_length % 8 != 0 else code
            code_bytes = int(padded_code, 2).to_bytes((len(padded_code) + 7) // 8, byteorder='big')
            f.write(code_bytes)
        f.write(encoded_bytes)

def read_compressed_file(filename):
    with open(filename, 'rb') as f:
        padding = int.from_bytes(f.read(1), byteorder='big')
        codebook_size = int.from_bytes(f.read(2), byteorder='big')
        codebook = {}
        for _ in range(codebook_size):
            char = int.from_bytes(f.read(1), byteorder='big')
            code_length = int.from_bytes(f.read(1), byteorder='big')
            code_bytes_length = (code_length + 7) // 8
            code_bytes = f.read(code_bytes_length)
            code_bits = ''.join(f"{byte:08b}" for byte in code_bytes)
            code = code_bits[:code_length]
            codebook[char] = code
        encoded_bytes = f.read()
    return encoded_bytes, codebook, padding


with open('HelpPane.exe', "rb") as f_in:
    data = f_in.read()
    encoded_bytes, codebook, padding = encode_huffman(data)
    write_compressed_file('HelpPane_ha_enc.exe', encoded_bytes, codebook, padding)

with open('HelpPane_ha_dec.exe', "wb") as f_out:
    encoded_bytes, codebook, padding = read_compressed_file('HelpPane_ha_enc.exe')
    decoded_data = decode_huffman(encoded_bytes, codebook, padding)
    f_out.write(decoded_data)

with open('HelpPane.exe', "rb") as f_in, open('HelpPane_ha_dec.exe', "rb") as f_out:
    original_data = f_in.read()
    decoded_data = f_out.read()
    if original_data == decoded_data:
        print("Проверка пройдена: исходные и декодированные данные совпадают.")
    else:
        print("Ошибочка: исходные и декодированные данные не совпадают.")
