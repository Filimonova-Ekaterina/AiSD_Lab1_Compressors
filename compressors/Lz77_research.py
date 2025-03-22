from collections import defaultdict
import math
import matplotlib.pyplot as plt


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

block_size = 32*1024
buffer_sizes = [1024, 2048, 4096, 8192, 16384, 32768] 
compression_ratios = []

for buffer_s in buffer_sizes:
    total_compressed_size = 0
    total_original_size = 0
    block_number = 0

    with open("Kuprin1.txt", "rb") as f_in:
        while True:
            block = f_in.read(block_size)
            if not block:
                break
            lz77_encoded = lz77_encode(block, buffer_s)
            total_compressed_size += len(lz77_encoded)
            total_original_size += len(block)
            block_number += 1
            print(f"Блок {block_number} закодирован с размером буфера {buffer_s}")

    average_compression_ratio = total_original_size/total_compressed_size
    compression_ratios.append(average_compression_ratio)
    print(f"Размер буфера: {buffer_s}, Средний коэффициент сжатия: {average_compression_ratio:.4f}")

plt.plot(buffer_sizes, compression_ratios, marker='o',markersize=4,color='k')
plt.xlabel('Размер буфера (байты)')
plt.ylabel('Коэффициент сжатия')
plt.savefig('lz77_2.png')
plt.show()

