import json
import os
import random
import re
import sys


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
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w') as fp:
        #son.dump(book, fp, indent=4)
        json.dump(book, fp)


def load(file_path, *key_books):
    if os.path.exists(file_path):
        rev_path = file_path.replace('.json', '_r.json')
        with open(file_path, 'r') as fp, open(rev_path, 'r') as fp2:
            return json.load(fp2), json.load(fp)
    else:
        global pages, page_number, line_window, line_number, char_window
        pages = {}
        page_number = 0
        line_window = {}
        line_number = 0
        char_window = []

        process_books(*key_books)
        rev_path = file_path.replace('.json', '_r.json')

        pages_str = {str(k): {str(k2): v2 for k2, v2 in v.items()}
        for k, v in pages.items()}

        save(rev_path, pages_str)
        code_book = generate_code_book()
        save(rev_path, code_book)
        return (pages_str, code_book)

def encrypt(code_book, message):
    cipher_text = []
    for char in message:
        if char not in code_book:
            raise ValueError(f"{char} is not in code_book")
        if len(code_book[char]) == 0:
            raise ValueError(f"No more positions available for '{char}")
        index = random.randint(0, len(code_book[char]) - 1)
        cipher_text.append(code_book[char].pop(index))
    return ':'.join(cipher_text)

def decrypt(rev_code_book, ciphertext):
    plaintext = []
    for cc in re.findall(r'\d+:\d+:\d+', ciphertext):
        page, line, char = cc.split(':')
        plaintext.append(rev_code_book[page][line][int(char)])
    return ''.join(plaintext)

def main_menu():
    print("""1). Encrypt
2). Decrypt
3). Quit
""");
    return int(input("Make a selection [1,2,3]: "))


def main():
    key_books = ('books/War_and_Peace.txt', 'books/Moby_Dick.txt', 'books/Dracula.txt')
    code_book_path = 'code_books/dmdwp.json'

    while True:
        try:
            choice = main_menu()
            if choice == 1:
                rev_code_book, code_book = load(code_book_path, *key_books)
                message = input("Enter secret message: ")
                encrypted = encrypt(code_book, message)
                print(f"Encrypted message: {encrypted}")
            elif choice == 2:
                rev_code_book, code_book = load(code_book_path, *key_books)
                message = input("Enter your cipher text: ")
                decrypted = decrypt(rev_code_book, message)
                print(f"Decrypted message: {decrypted}")
            elif choice == 3:
                sys.exit(0)
            else: print("Invalid selection")
        except ValueError as ve:
            print(f"ValueError: {ve}")
        except KeyError as ke:
            print(f"KeyError: {ke}")
        except Exception as e:
            print(f"Exception: {e}")



if __name__ == '__main__':
    main()


#p, cb = load('./code_books/book1.json', './books/love_song.txt')
#print(decrypt(p, '1:5:101:1:5:58:1:29:35:1:44:27-1:3:48:1:32:79'))

#print(len(p), len(cb))
#process_books('love_song'.txt')
#print(json.dumps(generate_code_book(), indent=4))
#print(json.dumps(pages, indent=4))
