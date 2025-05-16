
"""
Реализована инвертированная структура индекса, и индекс сжимается с использованием Elias Gamma и Elias Delta.
"""

import re

def build_inverted_index(documents):
    """
    Построить инвертированный индекс: Входная коллекция документов (словарь: doc_id -> текстовая строка),
Вывести инвертированный индекс (словарь: термин -> отсортированный список doc_id).
    """
    inverted_index = {}
    for doc_id, text in documents.items():

        words = re.findall(r'\w+', text.lower())
        for term in words:
            if term not in inverted_index:
                inverted_index[term] = []

            if len(inverted_index[term]) == 0 or inverted_index[term][-1] != doc_id:
                inverted_index[term].append(doc_id)

    for term in inverted_index:
        inverted_index[term] = sorted(set(inverted_index[term]))
    return inverted_index

def elias_gamma_encode(n):
    """
    Elias Gamma кодирует положительное целое число n (n >= 1) и
    возвращает его закодированную битовую строку (в виде строки).
    """
    if n <= 0:
        raise ValueError("Elias gamma coding is only defined for positive integers (n>=1)")
    binary = bin(n)[2:]
    N = len(binary) - 1
    prefix = '0' * N
    return prefix + binary

def elias_gamma_decode(bitstring):
    """
    Декодирование гаммы Элиаса: принимает в качестве входных данных
    объединенную битовую строку гаммы Элиаса и возвращает список декодированных целых чисел.
    """
    results = []
    i = 0
    n = len(bitstring)
    while i < n:

        count_zeros = 0
        while i < n and bitstring[i] == '0':
            count_zeros += 1
            i += 1
        if i >= n:
            break

        num_bits = count_zeros + 1
        if i + num_bits > n:
            break

        number_bits = bitstring[i: i + num_bits]
        i += num_bits

        number = int(number_bits, 2)
        results.append(number)
    return results

def elias_delta_encode(n):
    """
    Elias Delta кодирует положительное целое число n (n >= 1) и возвращает его закодированную битовую строку.
    """
    if n <= 0:
        raise ValueError("Elias gamma coding is only defined for positive integers (n>=1)")
    binary = bin(n)[2:]
    L = len(binary)

    gamma_L = elias_gamma_encode(L)

    offset = binary[1:] if L > 1 else ''
    return gamma_L + offset

def elias_delta_decode(bitstring):
    """
    Декодирование Elias Delta: принимает в качестве входных данных
    объединенную битовую строку Elias Delta и возвращает список декодированных целых чисел.
    """
    results = []
    i = 0
    n = len(bitstring)
    while i < n:

        count_zeros = 0
        while i < n and bitstring[i] == '0':
            count_zeros += 1
            i += 1
        if i >= n:
            break
        num_bits_L = count_zeros + 1
        if i + num_bits_L > n:
            break

        L_bits = bitstring[i: i + num_bits_L]
        i += num_bits_L
        L_val = int(L_bits, 2)

        if L_val - 1 > 0:
            if i + (L_val - 1) > n:
                break
            offset_bits = bitstring[i: i + (L_val - 1)]
            i += (L_val - 1)
        else:
            offset_bits = ''

        orig_binary = '1' + offset_bits
        value = int(orig_binary, 2)
        results.append(value)
    return results

def compress_index_gamma(inverted_index):
    """
    Сжать инвертированный индекс с помощью Elias Gamma (гамма-кодирование различий).
Возвращает: сжатый индекс (термин -> битовая строка).
    """
    compressed = {}
    for term, postings in inverted_index.items():

        prev = 0
        bits = ""
        for doc_id in postings:
            diff = doc_id - prev
            bits += elias_gamma_encode(diff)
            prev = doc_id
        compressed[term] = bits
    return compressed

def compress_index_delta(inverted_index):
    """
    Сожмите инвертированный индекс с помощью Elias Delta (дельта-кодирование различий).
Возвращает: сжатый индекс (термин -> битовая строка).
    """
    compressed = {}
    for term, postings in inverted_index.items():
        prev = 0
        bits = ""
        for doc_id in postings:
            diff = doc_id - prev
            bits += elias_delta_encode(diff)
            prev = doc_id
        compressed[term] = bits
    return compressed

def decompress_index_gamma(compressed_index):
    """
    Распаковать сжатый индекс Elias Gamma, вернув исходный инвертированный индекс (список терминов -> публикации).
    """
    inverted_index = {}
    for term, bitstring in compressed_index.items():

        diffs = elias_gamma_decode(bitstring)
        postings = []
        cum = 0
        for d in diffs:
            cum += d
            postings.append(cum)
        inverted_index[term] = postings
    return inverted_index

def decompress_index_delta(compressed_index):
    """
    Распаковать сжатый индекс Elias Delta, вернув исходный инвертированный индекс (список терминов -> публикации).
    """
    inverted_index = {}
    for term, bitstring in compressed_index.items():
        diffs = elias_delta_decode(bitstring)
        postings = []
        cum = 0
        for d in diffs:
            cum += d
            postings.append(cum)
        inverted_index[term] = postings
    return inverted_index


if __name__ == "__main__":

    documents = {
        1: "Hello world",
        2: "Hello",
        3: "world of python",
        4: "hello Python world"
    }
    # Построение инвертированного индекса
    index = build_inverted_index(documents)
    print("Оригинальный инвертированный индекс:")
    for term, postings in sorted(index.items()):
        print(f"  {term}: {postings}")
    # Индекс компрессии гамма-излучения Элиаса
    gamma_compressed = compress_index_gamma(index)
    print("\nИндекс гамма-сжатия (bitstring):")
    for term, bitstring in sorted(gamma_compressed.items()):
        print(f"  {term}: {bitstring}")
    # Индекс компрессии Элиаса Дельта
    delta_compressed = compress_index_delta(index)
    print("\nДельта-сжатый индекс (bitstring):")
    for term, bitstring in sorted(delta_compressed.items()):
        print(f"  {term}: {bitstring}")
    # Распакуйте и проверьте
    gamma_decompressed = decompress_index_gamma(gamma_compressed)
    delta_decompressed = decompress_index_delta(delta_compressed)
    print("\nПроверка гамма-декомпрессии:")
    for term, postings in sorted(gamma_decompressed.items()):
        print(f"  {term}: {postings} (правильный: {index[term]})")
    print("Гамма-декомпрессия соответствует исходному индексу:", gamma_decompressed == index)
    print("\nПроверка дельта-декомпрессии:")
    for term, postings in sorted(delta_decompressed.items()):
        print(f"  {term}: {postings} (правильный: {index[term]})")
    print("Соответствует ли дельта-декомпрессия исходному индексу:", delta_decompressed == index)
