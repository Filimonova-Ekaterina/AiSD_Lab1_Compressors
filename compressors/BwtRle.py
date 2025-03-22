def rle_encode(data,M):
    if not data:
        return b""
    encoded = bytearray()
    block_size =M//8
    count = 1
    repeat_flag=0
    prev_char = data[:block_size ]
    j=0
    data += b'\x00' * block_size 
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
    data += b'\x00'
    n = len(data)
    sa = build_suffix_array(data)
    last_column = bytearray(data[(sa[i] - 1) % n] for i in range(n))
    return bytes(last_column)

def bwt_decode(encoded_data):
    if not encoded_data:
        return b""
    S_index = encoded_data.find(b'\x00')
    if S_index == -1:
        print("Ошибка: не найдена строка, заканчивающаяся на \\x00")
        return b""
    last_column = list(encoded_data)
    P_inverse = counting_sort(last_column)
    N = len(last_column)
    S = bytearray()
    j = S_index
    for _ in range(N):
        j = P_inverse[j]
        S.append(last_column[j])
    return bytes(S).rstrip(b'\x00')


buffer_size = 1024
M = 8 #color = 24, gray = 8, bw = 8, enw = 16, kup=8, 1mb = 128
block_size = 1024

with open('HelpPane.exe', "rb") as f_in, open('HelpPane_br_enc.exe', 'wb') as f_out:
    block_number = 0
    while True:
        block = f_in.read(block_size)
        if not block:
            break
        bwt_encoded = bwt_encode(block)
        rle_encoded = rle_encode(bwt_encoded, M)
        metadata = f"Block={block_number},M={M},Size={len(rle_encoded)}"
        f_out.write(metadata.encode('utf-8') + b'\n')
        f_out.write(rle_encoded)
        block_number += 1

with open('HelpPane_br_enc.exe', 'rb') as f_in, open('HelpPane_br_dec.exe', 'wb') as f_out:
    while True:
        metadata = f_in.readline().decode('utf-8').strip()
        if not metadata:
            break
        block_number = int(metadata.split(',')[0].split('=')[1])
        M_from_file = int(metadata.split(',')[1].split('=')[1])
        block_size_encoded = int(metadata.split(',')[2].split('=')[1])
        encoded_block = f_in.read(block_size_encoded)
        if not encoded_block:
            continue
        rle_decoded = rle_decode(encoded_block, M_from_file)
        if b'\x00' not in rle_decoded:
            rle_decoded += b'\x00'
        bwt_decoded = bwt_decode(rle_decoded)
        f_out.write(bwt_decoded)

with open('HelpPane.exe', "rb") as f_in, open('HelpPane_br_dec.exe', 'rb') as f_out:
    original_data = f_in.read()
    decoded_data = f_out.read()
    if original_data == decoded_data:
        print("Проверка пройдена: исходные и декодированные данные совпадают.")
    else:
        print("Ошибка: исходные и декодированные данные не совпадают.")