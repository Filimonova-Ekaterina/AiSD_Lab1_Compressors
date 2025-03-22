from collections import defaultdict

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

#bw gray 64 kup 16
block_size= 64*1024
buffer_size = 64*1024
with open('HelpPane.exe', "rb") as f_in, open('HelpPane_lz77_enc.exe', "wb") as f_out:
        block_number = 0
        while True:
            block = f_in.read(block_size)
            if not block:
                break
            lz77_encoded = lz77_encode(block, buffer_size)
            metadata = f"Block={block_number},BufferSize={buffer_size},Size={len(lz77_encoded)}"
            f_out.write(metadata.encode('utf-8') + b'\n')
            f_out.write(lz77_encoded)
            block_number += 1
            print("Закодирован")
        
print("Закодирован")
with open('HelpPane_lz77_enc.exe', "rb") as f_in, open('HelpPane_lz77_dec.exe', "wb") as f_out:
    while True:
        metadata = f_in.readline().decode('utf-8').strip()
        if not metadata:
            break
        block_number = int(metadata.split(',')[0].split('=')[1])
        buffer_size = int(metadata.split(',')[1].split('=')[1])
        block_size_encoded = int(metadata.split(',')[2].split('=')[1])
        encoded_block = f_in.read(block_size_encoded)
        if not encoded_block:
            continue
        decoded_block = lz77_decode(encoded_block, buffer_size)
        f_out.write(decoded_block)

with open('HelpPane.exe', "rb") as f_in, open('HelpPane_lz77_dec.exe', "rb") as f_out:
    original_data = f_in.read()
    decoded_data = f_out.read()
    if original_data == decoded_data:
        print("Проверка пройдена: исходные и декодированные данные совпадают.")
    else:
        print("Ошибочка: исходные и декодированные данные не совпадают.")