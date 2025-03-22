def lz78_encode(data):
    dictionary = {b'': 0}
    current_string = b''
    encoded_data = []
    for byte in data:
        new_string = current_string + bytes([byte])
        if new_string in dictionary:
            current_string = new_string
        else:
            encoded_data.append((dictionary[current_string], byte))
            dictionary[new_string] = len(dictionary)
            current_string = b''
    if current_string:
        encoded_data.append((dictionary[current_string], 0))
    byte_array = bytearray()
    for index, byte in encoded_data:
        byte_array.extend(index.to_bytes(2, 'big'))
        byte_array.append(byte) 
    return bytes(byte_array)

def lz78_decode(encoded_data):
    dictionary = {0: b''}
    decoded_data = bytearray()
    i = 0
    
    while i < len(encoded_data):
        index = int.from_bytes(encoded_data[i:i+2], 'big')
        byte = encoded_data[i+2]
        i += 3
        if index in dictionary:
            new_entry = dictionary[index] + (bytes([byte]) if byte != 0 else b'')
        else:
            new_entry = bytes([byte]) if byte != 0 else b''
        
        decoded_data.extend(new_entry)
        dictionary[len(dictionary)] = new_entry
    
    return bytes(decoded_data)

block_size= 1024

with open('HelpPane.exe', "rb") as f_in, open('HelpPane_lz78_enc.exe', "wb") as f_out:
        block_number = 0
        while True:
            block = f_in.read(block_size)
            if not block:
                break
            lz78_encoded = lz78_encode(block)
            metadata = f"Block={block_number},Size={len(lz78_encoded)}"
            f_out.write(metadata.encode('utf-8') + b'\n')
            f_out.write(lz78_encoded)
            block_number += 1

        
print("Закодирован")
with open('HelpPane_lz78_enc.exe', "rb") as f_in, open('HelpPane_lz78_dec.exe', "wb") as f_out:
    while True:
        metadata = f_in.readline().decode('utf-8').strip()
        if not metadata:
            break
        block_number = int(metadata.split(',')[0].split('=')[1])
        block_size_encoded = int(metadata.split(',')[1].split('=')[1])
        encoded_block = f_in.read(block_size_encoded)
        if not encoded_block:
            continue
        decoded_block = lz78_decode(encoded_block)
        f_out.write(decoded_block)

with open('HelpPane.exe', "rb") as f_in, open('HelpPane_lz78_dec.exe', "rb") as f_out:
    original_data = f_in.read()
    decoded_data = f_out.read()
    if original_data == decoded_data:
        print("Проверка пройдена: исходные и декодированные данные совпадают.")
    else:
        print("Ошибочка: исходные и декодированные данные не совпадают.")
