import math
import matplotlib.pyplot as plt
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

def entropy(string, leng):
    if (leng<=0):
        print("Ошибка: длина кода символа должна быть положительной")
        return 0
    if (len(string)%leng!=0):
        string+= b'\x00'*((leng - (len(string)%leng))%leng)
    
    symbols = [string[i:i+leng] for i in range(0,len(string),leng)]
    freq = {}
    for symbol in symbols:
        if symbol in freq:
            freq[symbol]+=1
        else:
            freq[symbol]=1
    entrop=0.0
    len_symb = len(symbols)
    for count in freq.values():
        probability = count/len_symb
        entrop-= probability*math.log2(probability)
    return entrop

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

block_sizes = [256, 512, 1024, 2048, 4096, 8192, 16384]
entropies = []

for block_s in block_sizes:
    with open("enwik7", "rb") as f_in:
        total_entropy = 0
        block_number = 0
        while True:
            block = f_in.read(block_s)
            if not block:
                break
            bwt_encoded = bwt_encode(block)
            mtf_encoded = mtf_encode(bwt_encoded)
            current_entropy = entropy(mtf_encoded, 1)
            total_entropy += current_entropy
            block_number += 1
        average_entropy = total_entropy / block_number
        entropies.append(average_entropy)
        print(block_s, ' ', average_entropy)
plt.plot(block_sizes, entropies, marker='o',markersize=4,color='k')
plt.xlabel('Размер блока (байты)')
plt.ylabel('Энтропия')
plt.savefig('1.png')
plt.show()
