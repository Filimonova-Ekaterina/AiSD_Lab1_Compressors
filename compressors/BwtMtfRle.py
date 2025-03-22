def rle_encode(data, M):
    if not data:
        return b""
    encoded = bytearray()
    block_size = M // 8
    count = 1
    repeat_flag = 0
    prev_char = data[:block_size]
    j = 0
    data += b'\xFF' * block_size
    i = block_size
    while i < len(data):
        char = data[i:i + block_size]
        if char == prev_char and count < 127:
            count += 1
            i += block_size
            repeat_flag = 1
        else:
            if repeat_flag == 1:
                encoded.append(count)
                encoded.extend(prev_char)
                count = 1
                repeat_flag = 0
                prev_char = char
                i += block_size
            else:
                j = 0
                dop_str = bytearray()
                while char != prev_char and j < 127 and i + j * block_size < len(data):
                    j += 1
                    dop_str.extend(prev_char)
                    prev_char = char
                    char = data[i + j * block_size:i + j * block_size + block_size] if i + j * block_size < len(data) else b''
                encoded.append(j | 0x80)
                encoded.extend(dop_str)
                i += j * block_size
    return bytes(encoded)

def rle_decode(data, M):
    if not data:
        return b""
    decoded = bytearray()
    i = 0
    block_size = M // 8
    while i < len(data):
        count = data[i]
        if count & 0x80:
            length = count & 0x7F
            decoded.extend(data[i + 1:i + 1 + length * block_size])
            i += 1 + length * block_size
        else:
            char = data[i + 1:i + 1 + block_size]
            decoded.extend(char * count)
            i += 1 + block_size
    return bytes(decoded)

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
M = 8  # color = 24, gray = 8, bw = 8, enw = 16, kup=8, 1mb = 128
block_size = 1024

def process_file(filename, block_size=16 * 1024, M=8):
    with open(filename, 'rb') as f:
        data = f.read()
    blocks = [data[i:i + block_size] for i in range(0, len(data), block_size)]
    encoded_blocks = []
    block_lengths = []
    for block in blocks:
        bwt_encoded = bwt_encode(block)
        mtf_encoded = mtf_encode(bwt_encoded)
        rle_encoded = rle_encode(mtf_encoded, M)
        encoded_blocks.append(rle_encoded)
        block_lengths.append(len(rle_encoded))

    combined_data = b''.join(encoded_blocks)
    compressed_filename = 'color_bmr_enc.raw'
    with open(compressed_filename, 'wb') as f:
        f.write(len(blocks).to_bytes(4, byteorder='big'))
        for length in block_lengths:
            f.write(length.to_bytes(4, byteorder='big'))
        f.write(combined_data)

    with open(compressed_filename, 'rb') as f:
        num_blocks = int.from_bytes(f.read(4), byteorder='big')
        block_lengths_read = [int.from_bytes(f.read(4), byteorder='big') for _ in range(num_blocks)]
        encoded_data = f.read()

    decoded_blocks = []
    start = 0
    for length in block_lengths_read:
        end = start + length
        decoded_blocks.append(encoded_data[start:end])
        start = end

    original_blocks = []
    for block in decoded_blocks:
        rle_decoded = rle_decode(block, M)
        mtf_decoded = mtf_decode(rle_decoded)
        bwt_decoded = bwt_decode(mtf_decoded)
        original_blocks.append(bwt_decoded)
    original_data = b''.join(original_blocks)
    decompressed_filename = 'color_bmr_dec.raw'
    with open(decompressed_filename, 'wb') as f:
        f.write(original_data)

    print(f"Файл '{filename}' успешно обработан. Результат записан в '{compressed_filename}' и '{decompressed_filename}'.")
    with open(filename, 'rb') as f_out, open(decompressed_filename, 'rb') as f_in:
        dec = f_out.read()
        init = f_in.read()
        if dec == init:
            print('победа')
        else:
            print('во блин')

process_file('color.raw')
