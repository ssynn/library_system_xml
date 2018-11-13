'''
所有有关数据的操作全部集中在这个文件中
以xml实现的简易数据库
'''
import time
from lxml import etree

STUDENT_KEY = ['SID', 'PASSWORD', 'SNAME', 'DEPARTMENT', 'MAJOR', 'MAX']
BOOK_KEY = ['BID', 'BNAME', 'AUTHOR', 'PUBLICATION_DATE',
            'PRESS', 'POSITION', 'SUM', 'NUM']
BORROW_KEY = ['BID', 'SID', 'BORROW_DATE', 'DEADLINE', 'PUNISH']
LOG_KEY = ['BID', 'SID', 'BORROW_DATE', 'BACK_DATE', 'PUNISHED']
KEY = {
    'student': STUDENT_KEY,
    'book': BOOK_KEY,
    'borrowing_book': BORROW_KEY,
    'log': LOG_KEY
}


def list_to_nodetree(node_list: list, tag: str):
    '''
    传入二维列表[[,,...],...]
    返回ElementTree
    <nodes>
        <node>
            <tag1></tag1>
            <tag2></tag2>
            ...
        </node>
        ...
    </nodes>
    '''
    nodes = etree.Element(tag)
    tag = tag[:-1]
    for i in node_list:
        nodes.append(list_to_node(i, tag))
    return nodes


def list_to_node(info: list, tag: str):
    '''
    传入一维数组，类型，返回Element
    <node>
        <tag1></tag1>
        <tag2></tag2>
        ...
    </node>
    '''
    key_list = KEY[tag]
    node = etree.Element(tag)
    for key, text in zip(key_list, info):
        item = etree.Element(key)
        item.text = text
        node.append(item)
    return node


def nodetree_to_list(nodetree):
    '''
    传入ElementTree
    <nodes>
        <node>
            <tag1></tag1>
            <tag2></tag2>
            ...
        </node>
        ...
    </nodes>
    返回[[ , ,...],...]
    '''
    ans = []
    for node in nodetree.getchildren():
        temp = []
        for item in node.getchildren():
            temp.append(item.text)
        ans.append(temp)
    return ans


def open_database() -> dict:
    '''
    打开数据库
    返回database{
        'student':[[SID, PASSWORD, SNAME, DEPARTMENT, MAJOR, MAX],...],
        'book':[[BID, BNAME, AUTHOR, PUBLICATION_DATE, PRESS, POSITION, SUM, NUM],...],
        'borrowing_book':[[BID, SID, BORROW_DATE, DEADLINE, PUNISH],...],
        'log':[[BID, SID, BORROW_DATE, BACK_DATE, PUNISHED],...]
    }
    '''
    try:
        doc = etree.parse('data/database.xml')
        root = doc.getroot()
        children = root.getchildren()
        ans = {}
        for nodetree in children:
            ans[nodetree.tag] = nodetree_to_list(nodetree)
    except Exception as e:
        print('Open error')
        print(e)
        ans = None
    finally:
        return ans


def close_database(data: dict):
    '''
    关闭数据库
    传入database{
        'student':[[SID, PASSWORD, SNAME, DEPARTMENT, MAJOR, MAX],...],
        'book':[[BID, BNAME, AUTHOR, PUBLICATION_DATE, PRESS, POSITION, SUM, NUM],...],
        'borrowing_book':[[BID, SID, BORROW_DATE, DEADLINE, PUNISH],...],
        'log':[[BID, SID, BORROW_DATE, BACK_DATE, PUNISHED],...]
    }
    返回bool
    '''
    try:
        ans = True
        database = etree.Element('database')
        database.append(list_to_nodetree(data['students'], 'students'))
        database.append(list_to_nodetree(data['books'], 'books'))
        database.append(list_to_nodetree(data['borrowing_books'], 'borrowing_books'))
        database.append(list_to_nodetree(data['logs'], 'logs'))
        database = database.getroottree()
        database.write('data/database.xml')
    except Exception as e:
        print('Close error')
        print(e)
        ans = False
    finally:
        return ans


# 去掉字符串末尾的0
def remove_zero(val):
    while len(val) != 0 and val[-1] == ' ':
        val = val[:-1]
    return val


# 将元组列表转换为字典
def convert(val: list):
    if len(val) == 0:
        return None
    val = val[0]
    # 如果是学生
    if len(val) == 5:
        ans = {
            'class': 'stu',
            'SID': remove_zero(val[0]),
            'SNAME': remove_zero(val[1]),
            'DEPARTMENT': remove_zero(val[2]),
            'MAJOR': remove_zero(val[3]),
            'MAX': val[4]
        }
    else:
        ans = {
            'class': 'admin',
            'AID': remove_zero(val[0])
        }
    return ans


# 把书的元组列表转换为字典
def convert_book(val: tuple) -> dict:
    key_list = ['BID', 'BNAME', 'AUTHOR', 'PUBLICATION_DATE', 'PRESS', 'POSITION', 'SUM', 'NUM']
    ans = {}
    for i, key in zip(val, key_list):
        ans[key] = str(i)
    return ans


# 将日期延后两个月
def postpone(start: str):
    temp = start.split('-')
    temp[0] = int(temp[0])
    temp[1] = int(temp[1])
    temp[1] += 2
    if temp[1] > 12:
        temp[1] -= 12
        temp[0] += 1
    ans = '{:d}-{:0>2d}-{}-{}'.format(temp[0], temp[1], temp[2], temp[3])
    return ans


# 两个日期之间间隔的天数
def days_between(start: str, end: str):
    start = start.split('-')
    end = end.split('-')
    start[0] = int(start[0])
    start[1] = int(start[1])
    start[2] = int(start[2])

    end[0] = int(end[0])
    end[1] = int(end[1])
    end[2] = int(end[2])

    s = start[0]*365+start[1]*30+start[2]
    e = end[0]*365+end[1]*30+end[2]
    return e-s


# 注册
def signup(user_message: dict) -> bool:
    '''
    传入以下格式的字典
    user_message{
        'SID': str,
        'PASSWORD': str,
        'SNAME': str,
        'DEPARTMENT': str,
        'MAJOR': str,
        'MAX': int
    }
    '''
    res = True
    try:
        database = open_database()
        students = database['students']
        for i in students:
            if i[0] == user_message['SID']:
                raise Exception('用户已存在!')
        new_student = [
            user_message['SID'],
            user_message['PASSWORD'],
            user_message['SNAME'],
            user_message['DEPARTMENT'],
            user_message['MAJOR'],
            str(user_message['MAX'])
        ]
        students.append(new_student)
        close_database(database)
    except Exception as e:
        print('Signup error!')
        print(e)
        res = False
    finally:
        return res


# 登录
def signin(user_message: dict) -> dict:
    '''
    传入以下格式的字典
    user_message{
        'ID': str,
        'PASSWORD': str
    }
    如果管理员用户存在返回以下字典
    {
        'class': 'admin'
        'AID': str
    }
    如果学生用户存在返回以下格式的字典
    {
        'class': 'stu'
        'SID': str,
        'SNAME': str,
        'DEPARTMENT': str,
        'MAJOR': str,
        'MAX': int
    }
    否则返回None
    '''
    ans = None
    try:
        database = open_database()
        students = database['students']
        # 现在administrator表内匹配
        if user_message['ID'] == 'admin' and user_message['PASSWORD'] == '123456':
            temp = [(user_message['ID'],)]
        else:
            temp = []
        # 管理员表内没有找到则在student表内匹配
        if len(temp) == 0:
            for stu in students:
                if stu[0] == user_message['ID'] and stu[1] == user_message['PASSWORD']:
                    temp = [(stu[0], stu[2], stu[3], stu[4], int(stu[5]))]
                    break
        ans = temp
    except Exception as e:
        print('Signin error!')
        print(e)
    finally:
        return convert(ans)


# 更新学生信息
def update_student(user_message: dict) -> bool:
    '''
    传入字典格式如下
    user_message{
        'SID': str,
        'PASSWORD': str,
        'SNAME': str,
        'DEPARTMENT': str,
        'MAJOR': str,
        'MAX': int
    }
    返回bool
    '''
    try:
        res = False
        database = open_database()
        students = database['students']
        for stu in students:
            if stu[0] == user_message['SID']:
                stu[2] = user_message['SNAME']
                stu[3] = user_message['DEPARTMENT']
                stu[4] = user_message['MAJOR']
                stu[5] = str(user_message['MAX'])
                if 'PASSWORD' in user_message:
                    stu[1] = user_message['PASSWORD']
                    res = True
        close_database(database)
    except Exception as e:
        print('Update error!')
        print(e)
    finally:
        return res


# 获取学生信息
def get_student_info(SID: str) -> dict:
    '''
    传入SID
    返回stu_info{
        'class': stu,
        'SID': str,
        'SNAME': str,
        'DEPARTMENT': str,
        'MAJOR': str,
        'MAX': int
    }
    没找到返回None
    '''
    try:
        database = open_database()
        students = database['students']
        temp = []
        for stu in students:
            if stu[0] == SID:
                temp = [(stu[0], stu[2], stu[3], stu[4], int(stu[5]))]
                break
        ans = temp
    except Exception as e:
        print(e)
        print('get student info error')
        ans = []
    finally:
        if ans == []:
            return None
        return convert(ans)


# 查找学生
def search_student(info: str):
    '''
    传入SID或学生姓名进行查找
    返回[[SID, SNAME, DEPARTMENT, MAJOR, MAX],...]
    '''
    try:
        import re
        database = open_database()
        students = database['students']
        res = []
        val = info.split()
        val = [(i, '.*'+i+'.*') for i in val]
        # 显示所有书信息
        if info == 'ID/姓名' or info == '':
            for stu in students:
                stu.pop(1)
                stu[-1] = int(stu[-1])
            res = students
        else:
            # 按条件查找
            for i in val:
                for stu in students:
                    if stu[0] == i[0] or re.match(i[1], stu[2]):
                        temp = (stu[0], stu[2], stu[3], stu[4], int(stu[5]))
                        res.append(temp)
            res = list(set(res))
        temp = []
        for i in res:
            temp_ = []
            for j in range(4):
                temp_.append(remove_zero(i[j]))
            temp_.append(i[4])
            temp.append(temp_)
        res = temp
    except Exception as e:
        print('Search student error!')
        print(e)
        res = []
    finally:
        return res


# 删除学生信息
def delete_student(SID: str) -> bool:
    '''
    传入SID
    删除student表内记录,
    找出book表内所借的书强制还书
    删除log表内的记录
    '''
    try:
        res = True
        database = open_database()
        students = database['students']
        borrowing_books = database['borrowing_books']
        books = database['books']
        logs = database['logs']
        remove_borrowing_books = []
        remove_logs = []
        # 先强制把书还掉并记录borrowing_books中需要删除的行
        for borrowing_book in borrowing_books:
            if borrowing_book[1] == SID:
                for book in books:
                    if book[0] == borrowing_book[0]:
                        book[-1] = str(int(book[-1]) + 1)
                        break
                remove_borrowing_books.append(borrowing_book)
        # 记录logs中需要删除的行
        for log in logs:
            if log[1] == SID:
                remove_logs.append(log)
        # 删除学生表内的记录
        for stu in students:
            if stu[0] == SID:
                students.remove(stu)
                break
        # 删除borrowing_book的记录
        for i in remove_borrowing_books:
            borrowing_books.remove(i)
        # 删除log表内的记录
        for i in remove_logs:
            logs.remove(i)
        close_database(database)
    except Exception as e:
        print('delete book error!')
        print(e)
        res = False
    finally:
        return res


# 获取学生的借书信息
def get_borrowing_books(ID: str, BID: bool = False) -> list:
    '''
    当BID为False以SID的方式查找否则以BID查找
    返回此学生在借的书籍列表信息
    [[SID, BID, BNAME, BORROW_DATE, DEADLINE, PUNISH, NUM],[...],....]
    '''
    try:
        res = []
        database = open_database()
        borrowing_books = database['borrowing_books']
        books = database['books']
        if ID == '' or ID == 'ID/姓名':
            for book in books:
                for borrowing_book in borrowing_books:
                    if book[0] == borrowing_book[0]:
                        res.append((borrowing_book[1], book[0], book[1], borrowing_book[2], borrowing_book[3], int(borrowing_book[4]), int(book[-1])))
        elif BID:
            for book in books:
                for borrowing_book in borrowing_books:
                    if book[0] == ID and book[0] == borrowing_book[0]:
                        res.append((borrowing_book[1], book[0], book[1], borrowing_book[2], borrowing_book[3], int(borrowing_book[4]), int(book[-1])))
        else:
            for book in books:
                for borrowing_book in borrowing_books:
                    if borrowing_book[1] == ID and book[0] == borrowing_book[0]:
                        res.append((borrowing_book[1], book[0], book[1], borrowing_book[2], borrowing_book[3], int(borrowing_book[4]), int(book[-1])))
        temp = []
        for i in res:
            temp_ = []
            for j in range(5):
                temp_.append(remove_zero(i[j]))
            temp_.append(i[5])
            temp_.append(i[6])
            temp.append(temp_)
        res = temp
    except Exception as e:
        print('get borrowing books error!')
        print(e)
        res = []
    finally:
        return res


# 还书
def return_book(BID: str, SID: str) -> bool:
    '''
    传入BID, SID，删除borrowing_book表内的记录在log表内新建记录
    返回bool型
    '''
    try:
        res = True
        database = open_database()
        borrowing_books = database['borrowing_books']
        books = database['books']
        logs = database['logs']
        for borrowing_book in borrowing_books:
            if borrowing_book[0] == BID and borrowing_book[1] == SID:
                borrowing_book[3] = time.strftime("%Y-%m-%d-%H:%M")
                logs.append(borrowing_book)
                borrowing_books.remove(borrowing_book)
                for book in books:
                    if book[0] == BID:
                        book[-1] = str(int(book[-1]) + 1)
                        break
                break
        close_database(database)
    except Exception as e:
        print('Return error!')
        print(e)
        res = False
    finally:
        return res


# 交罚金
def pay(BID: str, SID: str, PUNISH: int) -> bool:
    '''
    传入BID, SID, PUNISH把当前数的DEADLINE往后延长两个月
    返回bool型
    '''
    try:
        res = True
        database = open_database()
        borrowing_books = database['borrowing_books']
        for borrowing_book in borrowing_books:
            if borrowing_book[0] == BID and borrowing_book[1] == SID:
                borrowing_book[3] = postpone(time.strftime('%Y-%m-%d-%H:%M'))
                borrowing_book[4] = str(int(borrowing_book[4])+PUNISH)
        close_database(database)
    except Exception as e:
        print('Pay error!')
        print(e)
        res = False
    finally:
        return res


# 获取历史记录
def get_log(ID: str, BID: bool = False) -> list:
    '''
    传入SID
    返回[[SID, BID, BNAME, BORROW_DATE, BACK_DATE, PUNISHED],...]
    '''
    try:
        res = []
        database = open_database()
        logs = database['logs']
        books = database['books']
        if ID == '' or ID == 'ID/姓名':
            for book in books:
                for log in logs:
                    if book[0] == log[0]:
                        res.append((log[1], log[0], book[1], log[2], log[3], int(log[4])))
        elif BID:
            for book in books:
                for log in logs:
                    if log[0] == ID and book[0] == log[0]:
                        res.append((log[1], log[0], book[1], log[2], log[3], int(log[4])))
        else:
            for book in books:
                for log in logs:
                    if log[1] == ID and book[0] == log[0]:
                        res.append((log[1], log[0], book[1], log[2], log[3], int(log[4])))
    except Exception as e:
        print('get log error!')
        print(e)
        res = []
    finally:
        temp = []
        for i in res:
            temp_ = []
            for j in range(5):
                temp_.append(remove_zero(i[j]))
            temp_.append(i[5])
            temp.append(temp_)
        temp.sort(key=lambda x: x[4])
        return temp


# 加入新书
def new_book(book_info: dict) -> bool:
    '''
    传入以下格式的字典
    book_msg{
        'BID': str,
        'BNAME': str,
        'AUTHOR': str,
        'PUBLICATION_DATE': str,
        'PRESS': str,
        'POSITION': str,
        'SUM': int
    }
    返回bool
    '''
    res = True
    try:
        database = open_database()
        books = database['books']
        for book in books:
            if book[0] == book_info['BID']:
                raise Exception('书ID已存在!')
        books.append([
            book_info['BID'],
            book_info['BNAME'],
            book_info['AUTHOR'],
            book_info['PUBLICATION_DATE'],
            book_info['PRESS'],
            book_info['POSITION'],
            str(book_info['SUM']),
            str(book_info['SUM'])
        ])
        close_database(database)
    except Exception as e:
        print('add book error!')
        print(e)
        res = False
    finally:
        return res


# 获取书详细信息
def get_book_info(BID: str) -> dict:
    '''
    传入BID
    返回book_msg{
        'BID': str,
        'BNAME': str,
        'AUTHOR': str,
        'PUBLICATION_DATE': str,
        'PRESS': str,
        'POSITION': str,
        'SUM': int,
        'NUM': int
    }
    '''
    try:
        res = []
        books = open_database()['books']
        for book in books:
            if book[0] == BID:
                res = book
        if len(res) == 0:
            raise Exception('查无此书')
    except Exception as e:
        print('get book info error!')
        print(e)
        res = []
    finally:
        if res != []:
            res = convert_book(res)
        return res


# 更新书籍信息
def update_book(book_info: dict) -> bool:
    '''
    传入以下格式的字典
    book_msg{
        'BID': str,
        'BNAME': str,
        'AUTHOR': str,
        'PUBLICATION_DATE': str,
        'PRESS': str,
        'POSITION': str,
        'SUM': int,
        'NUM': int
    }
    返回bool
    '''
    try:
        res = True
        database = open_database()
        books = database['books']
        for book in books:
            if book[0] == book_info['BID']:
                book[1] = book_info['BNAME']
                book[2] = book_info['AUTHOR']
                book[3] = book_info['PUBLICATION_DATE']
                book[4] = book_info['PRESS']
                book[5] = book_info['POSITION']
                book[6] = str(book_info['SUM'])
                book[7] = str(book_info['NUM'])
                break
        close_database(database)
    except Exception as e:
        print('Update book error!')
        print(e)
        res = False
    finally:
        return res


# 删除书籍
def delete_book(BID: str) -> bool:
    '''
    传入BID
    返回bool
    会删除book，borrowing_book，log表内所有对应的记录
    '''
    try:
        res = True
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        cursor.execute('''
            DELETE
            FROM book
            WHERE BID=%s
            DELETE
            FROM borrowing_book
            WHERE BID=%s
            DELETE
            FROM log
            WHERE BID=%s
            ''', (BID, BID, BID))
        conn.commit()
    except Exception as e:
        print('delete book error!')
        print(e)
        res = False
    finally:
        conn.close()
        return res


# 搜索书籍
def search_book(mes: str, SID: str = '') -> list:
    '''
    可以传入BID或作者或出版或书名社进行查找
    返回[[BID, BNAME, AUTHOR, PUBLICATION_DATE, PRESS, POSITION, SUM, NUM, STATE],...]
    '''
    try:
        res = []
        val = mes.split()
        val = [('%'+i+'%', i, '%'+i+'%', '%'+i+'%') for i in val]
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()

        # 显示所有书信息
        if mes == 'ID/书名/作者/出版社' or mes == '':
            cursor.execute('''
            SELECT *
            FROM book
            ''')
        else:
            # 先把借书日期，书本剩余数量，罚金等信息找出
            cursor.executemany('''
            SELECT *
            FROM book
            WHERE PRESS LIKE %s OR BID=%s OR BNAME LIKE %s OR AUTHOR LIKE %s
            ''', val)

        res = cursor.fetchall()
        temp = []
        for i in res:
            temp_ = []
            for j in range(6):
                temp_.append(remove_zero(i[j]))
            temp_.append(i[6])
            temp_.append(i[7])
            temp.append(temp_)
        res = temp

        # 匹配学生信息判断每一本书是否可借
        if SID != '':
            cursor.execute('''
            SELECT MAX
            FROM student
            WHERE SID=%s
            ''', (SID))
            max_num = cursor.fetchall()[0][0]
            punish = False
            borrowing_book = get_borrowing_books(SID)
            for i in borrowing_book:
                if i[4] < time.strftime("%Y-%m-%d-%H:%M"):
                    punish = True
                    break
            for book in res:
                # 有罚金没交
                if punish:
                    book.append('未交罚金')
                    continue
                # 如果已经借的书达到上限就不再可借
                if len(borrowing_book) >= max_num:
                    book.append('借书达上限')
                    continue
                # 判断受否有此书
                for borrow in borrowing_book:
                    if book[0] == borrow[1]:
                        book.append('已借此书')
                        break
                if book[-1] != '已借此书':
                    book.append('借书')
    except Exception as e:
        print('Search error!')
        print(e)
        res = []
    finally:
        conn.close()
        return res


# 借书
def borrow_book(BID: str, SID: str) -> bool:
    '''
    传入BID和SID
    返回bool
    book的NUM减一
    在borrowing_book表内新建记录
    '''
    try:
        res = True
        conn = pymssql.connect(CONFIG['host'], CONFIG['user'], CONFIG['pwd'], CONFIG['db'])
        cursor = conn.cursor()
        # 先把借书日期，书本剩余数量，罚金等信息找出
        cursor.execute('''
        SELECT NUM
        FROM book
        WHERE BID=%s
        ''', (BID))
        book_mes = cursor.fetchall()
        # print(book_mes)
        NUM = book_mes[0][0]
        BORROW_DATE = time.strftime("%Y-%m-%d-%H:%M")
        DEADLINE = postpone(BORROW_DATE)

        # book表内NUM减一，新建borrowing_book表内的记录
        cursor.execute('''
        UPDATE book
        SET NUM=%d
        WHERE BID=%s
        INSERT
        INTO borrowing_book
        VALUES(%s, %s, %s, %s, 0)
        ''', (NUM-1, BID, BID, SID, BORROW_DATE, DEADLINE))
        conn.commit()

    except Exception as e:
        print('borrow error!')
        print(e)
        res = False
    finally:
        conn.close()
        return res


# 密码   为了调试方便就先不加密了
def encrypt(val):
    import hashlib
    h = hashlib.sha256()
    password = val
    h.update(bytes(password, encoding='UTF-8'))
    result = h.hexdigest()
    result = val
    return result


if __name__ == '__main__':
    temp = {
        'SID': '201602',
        'PASSWORD': '8d969eef6ecad3c29a3a629280e686cf0c3f5d5a86aff3ca12020c923adc6c92',
        'SNAME': '小王',
        'DEPARTMENT': '数学与信息科学学院',
        'MAJOR': 'SE',
        'MAX': 5
    }
    user_message = {
        'SID': '1',
        'SNAME': '1111',
        'PASSWORD': '1',
        'DEPARTMENT': '1',
        'MAJOR': '2',
        'MAX': 6
    }
    temp_login = {
        'ID': '1',
        'PASSWORD': '1'
    }
    book_msg = {
                'BID': '4',
                'BNAME': 'Java',
                'AUTHOR': 'kak',
                'PUBLICATION_DATE': '2019-05',
                'PRESS': '电子出版社',
                'POSITION': 'C0005',
                'SUM': 6,
                'NUM': 6
            }
    # 注册测试
    # print(signup(temp))

    # 还书测试
    # print(get_borrowing_books('1'))
    # print(return_book('1', '1'))
    # print(get_borrowing_books('1'))

    # 登录测试
    # print(signin({'ID': 'admin', 'PASSWORD': '123456'}))

    # 查书测试
    # print(search_book('ID/书名/作者/出版社'))

    # 推迟日期方法测试
    # print(postpone('2018-11-10-10:58'))

    # 借书测试
    # print(borrow_book('2', '1'))

    # 获取借书日志测试
    print(get_log('1', True))

    # 更新学生信息测试
    # print(update_student(user_message))

    # 加入新书测试
    # print(new_book(book_msg))

    # 获取书本详细信息
    # print(get_book_info('7'))

    # 删除书籍
    # print(delete_book('3'))

    # 查找学生
    # print(search_student(''))

    # 获取学生信息
    # print(get_student_info('20'))

    # 删除学生
    # print(delete_student('1'))

    # 初始化数据库
    # init_database()

    # 交罚金测试
    # pay('2', '1', 23)

    # 查书测试
    # print(get_book_info('4'))

    # 更新书籍测试
    print(update_book(book_msg))
