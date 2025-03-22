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


buffer_size = 1024
M = 8#color = 24, gray = 8, bw = 8, enw = 16, kup=8, 1mb = 128
block_size = 100*1024

with open('black_white.raw', "rb") as file_in:
    data = file_in.read()
encoded = rle_encode(data, M)
metadata = f"M={M}"
with open('black_white_rle_enc.raw', 'wb') as f:
        f.write(metadata.encode('utf-8') + b'\n')
        f.write(encoded)

with open('black_white_rle_enc.raw', 'rb') as f:
        metadata = f.readline().decode('utf-8').strip()
        encoded_str_from_file = f.read()
M_from_file = int(metadata.split('=')[1])
decoded_str = rle_decode(encoded_str_from_file, M_from_file).rstrip(b'\x00')
with open('black_white_rle_dec.raw', 'wb') as f:
    f.write(decoded_str)

if data == decoded_str:
    print("Проверка пройдена: исходные и декодированные данные совпадают.")
else: print ("Ошибочка")

#with open("enwik7", "rb") as f_in, open('enwik7_rle_enc', 'wb') as f_enc_w,open('enwik7_rle_enc', 'rb')\
#   as f_enc_r, open('enwik7_rle_dec','wb') as f_dec:
#    block_number = 0
#    while True and block_number<100:
#        block = f_in.read(block_size)
#        if not block:
#            break
#        print(f"Обработка блока {block_number}...")
#        #bwt_encoded = bwt_encode(block)
#        rle_encoded = rle_encode(block, M)
#        metadata = f"Block={block_number},M={M},Size={len(rle_encoded)}"
#        f_enc_w.write(metadata.encode('utf-8') + b'\n')
#        f_enc_w.write(rle_encoded)
#        metadata = f_enc_r.readline().decode('utf-8').strip()
#        if not metadata:
#            break
#        block_number = int(metadata.split(',')[0].split('=')[1])
#        M_from_file = int(metadata.split(',')[1].split('=')[1])
#        block_size_encoded = int(metadata.split(',')[2].split('=')[1])
#        encoded_block = f_enc_r.read(block_size_encoded)
#        if not encoded_block:
#            continue
#        rle_decoded = rle_decode(encoded_block, M_from_file)
#        #if b'\x00' not in rle_decoded:
#        #    rle_decoded += b'\x00'
#        #bwt_decoded = bwt_decode(rle_decoded)
#        #if block!=bwt_decoded:
#        #    print("УПС")
#        #    break
#        #else: print("+")
#        f_dec.write(rle_decoded)
#        block_number += 1

#with open("enwik7", "rb") as f_in, open('enwik7_rle_dec', 'rb') as f_out:
#    data = f_in.read()
#    out_data = f_out.read()
#    if data==out_data:
#        print('yes')
#    else:
#        print('wtf')