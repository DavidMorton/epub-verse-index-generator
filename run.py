from zipfile import ZipFile
import re
import pandas as pd
import datetime

file_name = '/Users/davidmorton/Downloads/Awake, Oh Sleeper! - David Morton.epub'
timestamp = datetime.datetime.isoformat(datetime.datetime.now()).replace('-', '').replace('T', '').replace(':','').split('.')[0]
output_file_name = f'/Users/davidmorton/Downloads/output_{timestamp}.epub'

regex = '((?:[123] )?[a-zA-Z]+) (\\d+)\\:(\\d+)(?:[-–](\\d+))?'

items = []

books = []
books_csv = pd.read_csv('books.csv')
booknames = books_csv.set_index('BookName')['BookID']
print(booknames)

def get_book_order(book:str):
    if book in booknames.keys():
        return booknames[book]
    return 0

def sanitize_book_name(book:str):
    otherbooks = {
        "Ps": "Psalms",
        "Psalm": "Psalms",
        "Isa": "Isaiah",
        'Eccl':'Ecclesiastes',
        'Dan':'Daniel',
        '1 Cor':'1 Corinthians',
        'Gen':'Genesis',
        'Rev':'Revelation',
        'Rom':'Romans',
        '1 Tim':'1 Timothy',
        'Matt':'Matthew',
        '1 Pet':'1 Peter',
        '2 Cor':'2 Corinthians',
        'Ge':'Genesis'
    }

    if book in otherbooks.keys():
        book = otherbooks[book]

    if book not in booknames.keys():
        print(f'Warning! {book} is not in booknames')
    return book

def divide_file(content:str):
    divisions = []

    start = 0
    matches = re.finditer(regex, content)

    for match in matches:
        groups = list(match.groups())
        book = sanitize_book_name(groups[0])
        book_order = get_book_order(book)
        chapter = int(groups[1])
        verse_start = int(groups[2])
        verse_end = verse_start if groups[3] is None else int(groups[3])

        reference = f"{book} {chapter}:{verse_start}{('' if verse_end == verse_start else (f'-{verse_end}'))}"

        ref_start = match.start()
        ref_end = match.end()
        divisions.append(content[start:ref_start])
        divisions.append((content[ref_start:ref_end], book_order, book, chapter, verse_start, verse_end, reference))
        start = ref_end

    divisions.append(content[start:])
        
    return divisions

def refigure_file(filename, divisions):
    output = ''
    references = []
    current_index = 1
    for x in divisions:
        if type(x) == str:
            output = output + x
        else:
            text, book_order, book, chapter, verse_start, verse_end, reference = x
            text = f"<a id='ref{current_index}'>{reference}</a>"
            output += text
            references += [(f'{filename}#ref{current_index}', book_order, book, chapter, verse_start, verse_end, reference)]
            current_index = current_index + 1

    return output, references
        

            

references = []
z = ZipFile(file_name)
output_zip = ZipFile(output_file_name, 'x')

for item in z.filelist:
    bcontent = z.read(item)
    if item.filename.endswith('.xhtml'):
        content = bcontent.decode('utf-8')
        divisions = divide_file(content)
        content, new_refs = refigure_file(item.filename, divisions)
        bcontent = bytes(content, 'utf-8')
        references += new_refs
    output_zip.writestr(item.filename, bcontent)


    



# items.sort()
# books.sort()
# books = list(set(books))
# books.sort()
# extraneousbooks = [x for x in books if x not in booknames]

# for x in items:
#     print(x)

# for x in extraneousbooks:
#     print(x)

#print(len(items))
        