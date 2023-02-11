from flask_cors import CORS
from flask import Flask, request
import psycopg2
import PyPDF2
import os


app = Flask('spend-analizer')
CORS(app)

url = "postgresql://postgres:hello@localhost/statements"
connection = psycopg2.connect(url)

CREATE_TABLE_NEW = (
    " ".join([
        'CREATE EXTENSION IF NOT EXISTS "uuid-ossp";',
        'CREATE TABLE IF NOT EXISTS users (id UUID DEFAULT uuid_generate_v4() PRIMARY KEY, name TEXT);',
        'CREATE TABLE IF NOT EXISTS users_ref_ids (id UUID DEFAULT uuid_generate_v4() PRIMARY KEY , user_id UUID ,name TEXT , ref_id TEXT);',
        'CREATE TABLE IF NOT EXISTS ref_details (id UUID DEFAULT uuid_generate_v4() PRIMARY KEY , name TEXT , description TEXT , ref_id TEXT);',
        'CREATE TABLE IF NOT EXISTS users_transactions (id UUID DEFAULT uuid_generate_v4() PRIMARY KEY , user_id UUID , name TEXT , date DATE , amount NUMERIC , type TEXT);',
        'CREATE TABLE IF NOT EXISTS statements (id UUID DEFAULT uuid_generate_v4() PRIMARY KEY , file_name TEXT , whole_line TEXT , date DATE , ref_id TEXT ,  ref TEXT , disc TEXT , amount NUMERIC , type TEXT);'
    ])
)


@app.get('/')
def home():
    return "hello world"


@app.get('/drop_table')
def drop_table():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute('DROP TABLE statements')
    return "table droped!"


@app.get('/create_table')
def create_table():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_TABLE_NEW)
    return "table created!"


@app.get('/get_statements')
def get_statements():
    with connection:
        with connection.cursor() as cur:
            cur.execute('SELECT * FROM statements')
            data = [dict((cur.description[i][0], value)
                         for i, value in enumerate(row)) for row in cur.fetchall()]
    return {"data": data}


@app.get('/get_statements_unique_ref_id')
def get_statements_unique_ref_id():
    with connection:
        with connection.cursor() as cur:
            cur.execute('SELECT DISTINCT ref_id FROM statements')
            #  = cur.fetchall()
            unique_ref_id = [list(value for i, value in enumerate(row))[
                0] for row in cur.fetchall()]
    return {"data": unique_ref_id}


@app.get('/get_statements_ref_id')
def get_statements_ref_id():
    args = request.args
    ref_id = args.get("ref_id")
    query = f"FROM statements WHERE ref_id = '{ref_id}' or ref in (SELECT DISTINCT ref FROM statements WHERE ref_id = '{ref_id}')"
    print(query)
    with connection:
        with connection.cursor() as cur:
            cur.execute(
                f"SELECT * {query}")

            # cur.execute('SELECT * FROM statements WHERE ref_id = 0000770 AND ref is not null')
            data = [dict((cur.description[i][0], value)
                         for i, value in enumerate(row)) for row in cur.fetchall()]

            cur.execute(
                f"SELECT SUM(amount) as total_amount {query}")

            total_amount = cur.fetchone()[0]

    return {"data": data, "total_amount": total_amount}


@app.get('/insert_data_form_pdf')
def insert_data_form_pdf():

    with connection:
        with connection.cursor() as cur:
            cur.execute('SELECT DISTINCT file_name FROM statements')
            #  = cur.fetchall()
            existing_file = [list(value for i, value in enumerate(row))[
                0] for row in cur.fetchall()]

            for file in os.listdir("statements"):
                if (not existing_file or file not in existing_file) and (file.endswith(".PDF") or file.endswith(".pdf")):
                    read_file_path = os.path.join("statements", file)

                    # try:
                    # creating a pdf file object
                    pdfFileObj = open(read_file_path, 'rb')

                    # creating a pdf reader object
                    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

                    # printing number of pages in pdf file
                    # print('No of pages - ', pdfReader.numPages)

                    account = list()
                    startPush = False

                    for x in range(pdfReader.numPages):
                        # print the result
                        # print(f"Page {x} of {pdfReader.numPages}")

                        # creating a page object
                        pageObj = pdfReader.getPage(x)

                        # extracting text from page
                        # for line in pageObj.extractText().splitlines():

                        startLineIdx = -1
                        for lineidx, line in enumerate(pageObj.extractText().splitlines()):

                            if line.find('Date  Transaction Description Amount (in Rs.)') != -1:
                                startLineIdx = lineidx + 3

                            if startLineIdx == lineidx:
                                startPush = True

                            if line.find('DUPLICATE STATEMENT') != -1 or line.find('Cash points waiting for you') != -1 or line.find('Reward Points Summary') != -1:
                                startPush = False

                            if startPush:
                                lineSplit = ' '.join(line.replace(
                                    'Millennia Credit Card Statement', '').strip().split(' ')).split()
                                lineObj = {'file_name': '', 'whole_line': '', 'date': '',
                                           'ref_id': '', 'ref': '', 'disc': '', 'amount': 0, 'type': ''}
                                lineObj['whole_line'] = line
                                lineObj['file_name'] = file
                                lineObj['date'] = lineSplit[0]
                                lineSplitIdx = len(lineSplit)

                                if lineSplit[lineSplitIdx - 1] == "Cr":
                                    lineObj['amount'] = lineSplit[lineSplitIdx - 2]
                                    lineObj['type'] = "credit"
                                else:
                                    lineObj['amount'] = lineSplit[lineSplitIdx - 1]
                                    lineObj['type'] = "debit"

                                lineObj['amount'] = lineObj['amount'].split('.')[
                                    0].replace(',', '')

                                if line.find('(Ref# ') != -1:
                                    lineObj['ref'] = line[line.find(
                                        '(Ref# ')+6:line.find(')')]
                                    lineObj['ref_id'] = line[line.find(
                                        '(Ref# ')-8:line.find('(Ref# ')-1]

                                    if lineObj['ref_id'].isnumeric():
                                        lineObj['ref_id'] = lineObj['ref_id']
                                    else:
                                        lineObj['ref_id'] = ''

                                if lineObj['amount'].isnumeric():
                                    lineObj['amount'] = int(lineObj['amount'])
                                else:
                                    lineObj['amount'] = 0

                                account.append(list(lineObj.values()))

                    # closing the pdf file object
                    pdfFileObj.close()

                    args_str = ','.join(cur.mogrify(
                        "(%s,%s,%s,%s,%s,%s,%s,%s)", x).decode('utf-8') for x in account)
                    cur.execute(
                        "INSERT INTO statements(file_name, whole_line, date, ref_id, ref, disc, amount, type) VALUES" + args_str)

    return "Data updated"
