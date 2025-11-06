import json
import os
import random
import re

HOW_MANY_BOOK = 3
LINE = 128
PAGE = 64
pages = {}
page_number=0
line_window = {}
line_number = 0
char_window = []

def clean_line(line):
    return line.strip().replace( '-', '' ) + ' '   # Adding a space instead of a newline.

def read_book(file_path):
    global char_window
    with open(file_path, 'r', encoding='utf-8-sig') as fp:
        for line in fp:
            line = clean_line(line)
            if line.strip():
                for c in line:
                    process_char(c)
    if len(char_window) > 0:
        add_line()
    if len(line_window) > 0:
        add_page()

def process_char(char):
    global char_window
    char_window.append(char)
    if len(char_window) == LINE:
        add_line()


def add_line():
    global char_window, line_number
    line_number += 1
    process_page( ''.join(char_window), line_number )
    char_window.clear()

def process_char(char):
    global char_window
    char_window.append(char)
    if len(char_window) == LINE:
        add_line()

def process_page(line, line_num):
    global line_window, pages, page_number
    line_window[line_num] = line
    if len(line_window) == PAGE:
        add_page()

def add_page():
    global line_number, line_window, pages, page_number
    page_number += 1
    pages[page_number] = dict(line_window)
    line_window.clear()
    line_number = 0

def process_books(*books):
    for book in books:
        read_book(book)


def generate_code_book():
    global pages
    code_book = {}
    for page, lines in pages.items():
        for num, line in lines.items():
            for pos, char in enumerate(line):
                if char in code_book:
                   code_book[char].append(f'{page}:{num}:{pos}')
                else:
                    code_book[char] = [f'{page}:{num}:{pos}']

    return code_book


def save(file_path, book):
    with open(file_path, 'w') as fp:
        #son.dump(book, fp, indent=4)
        json.dump(book, fp)


def load(file_path, *key_books):
    if os.path.exists(file_path):
        with open(file_path, 'r') as fp, open(file_path.replace('.json', '_r.json')) as fp2:
            return json.load(fp2), json.load(fp)
    else:
        process_books(*key_books)
        save(file_path.replace('.json', '_r.json'), pages)
        code_book = generate_code_book()
        save(file_path, code_book)
        return (pages, code_book)

def encrypt(code_book, message):
    cipher_text = []
    for char in message:
        index = random.randint(0, len(code_book[char]) - 1)
        cipher_text.append(code_book[char].pop(index))
    return ':'.join(cipher_text)

def decrypt(rev_code_book, ciphertext):
    plaintext = []
    for cc in re.findall(r'\d+:\d+:\d+', ciphertext):
        page, line, char = cc.split(':')
        plaintext.append(
            rev_code_book[page][line][int(char)])
    return ''.join(plaintext)



p, cb = load('./code_books/book1.json', './books/love_song.txt')
print(encrypt(cb, 'Let us'))
print(decrypt(p, '1:5:101:1:5:58:1:29:35:1:44:27-1:3:48:1:32:79'))

#print(len(p), len(cb))
#process_books('love_song'.txt')
#print(json.dumps(generate_code_book(), indent=4))
#print(json.dumps(pages, indent=4))
