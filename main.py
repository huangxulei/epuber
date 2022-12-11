# @Time:2022/11/6 10:57
# @Author: 赵阿贵
# @File:main.py
import sys, os, shutil
import sqlite3
from zipfile import ZipFile,BadZipfile
from xml.dom.minidom import parseString
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QFileDialog, QMessageBox, QGridLayout, QVBoxLayout, QLabel, QScrollArea,  QCheckBox, QHBoxLayout, QInputDialog, QLineEdit, QRadioButton, QButtonGroup ,QListWidgetItem, QDialog
from PyQt5.QtCore import QSize, Qt, pyqtSignal , QPoint
from PyQt5.QtGui import QPixmap , QMouseEvent ,QCursor, QGuiApplication
from CommonHelper import CommonHelper
from bookShow import bookShow
from functools import partial
from ncxHandler import ncxHandler
from xml import sax
import calendar
import time, re
from mainView import Ui_MainWindow
from PIL import Image
from io import BytesIO
from classfiy_dialog import AddDialog, EditDialog, AddBookClassfiy

class myLabel(QLabel):

    doubleclicked = pyqtSignal()
    def mouseDoubleClickEvent(self, QMouseEvent):

        if QMouseEvent.button() == Qt.LeftButton:
            self.doubleclicked.emit()

    def enterEvent(self, QMouseEvent):

        self.children()[0].show()

    def leaveEvent(self, QMouseEvent):

        if not self.children()[0].isChecked():
            self.children()[0].hide()

about_str = [
 '''\n \n1、本软件用于打开Epub文件的电子书阅读器。

2、开发相关

   开发工具：pycharm
   开发框架：基于python的组件pyqt5
   数据库：sqlite3

3、开发者：赵阿贵

   联系QQ：37156760
   交流QQ群：616712461
             ''',
 '''\n \n问题：
 
    1、导入有些epub文件的时候，会导致程序退出。
    
    原因：因为epub文件格式有好多，有些不是很标准的epub可能会出现问题。
    ''']

class index(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super(index, self).__init__()
        self.colors =  ['gray', 'black', 'red', 'blue', 'green', 'orange']
        self.init_db()
        self.setupUi(self)
        self.show()
        self.init_classfiylist()
        self.initBtn()
        self.init_booklist()

    def add_book_classfiy(self):

        AddBookClassfiy.get_add_dialog(self.getClassList(), self)

    def add_book_classfiy_db(self, index):

        cfid = self.getClassList()[index][0]
        instr = "("
        for i, v in enumerate(self.checkedList):
            instr += str(v['bookid'])
            if i != (len(self.checkedList)-1):
                instr += ","
        instr += ")"
        sql = f"update book set classfiy_id= {cfid} where book_id in {instr}"
        self.c.execute(sql)
        self.conn.commit()
        self.init_classfiylist()
        self.init_booklist()
        self.adddelwidget.hide()

    def getClassList(self):

        sql = "select * from classfiy"
        res =self.c.execute(sql)
        return res.fetchall()

    def add_classfiy(self):

        self.stackedWidget.setCurrentIndex(0)
        AddDialog.get_add_dialog(self)

    def edit_classfiy(self,cdata):

        self.stackedWidget.setCurrentIndex(0)
        EditDialog.get_edit_dialog(cdata, self)

    def save_classfiy(self, data):

        sql = f'INSERT INTO classfiy(classfiy_id, classfiy_name, classfiy_color) VALUES ( NULL, "{data[0]}", {data[1]})'
        self.c.execute(sql)
        self.conn.commit()
        self.init_classfiylist()

    def save_classfiy_db(self, data):

        sql = f"UPDATE classfiy SET classfiy_name ='{data[1]}', classfiy_color='{data[2]}' WHERE classfiy_id= {data[0]}"
        self.c.execute(sql)
        self.conn.commit()
        self.init_classfiylist()

    def del_classfiy(self, data):

       sql = f"DELETE FROM classfiy WHERE classfiy_id= {data[0]}"
       self.c.execute(sql)
       self.conn.commit()
       self.init_classfiylist()

    def init_classfiylist(self):

        sql = "select count(*) from book"
        res = self.c.execute(sql)
        self.allnum = res.fetchall()[0][0]
        self.allBook.setText(f" 全部书籍 （{str(self.allnum)}）")
        self.allBook.clicked.connect(partial(self.checkClassfiy, 0))
        sql = "select c.classfiy_id, c.classfiy_name, c.classfiy_color,  count(b.classfiy_id) num from (select * from classfiy) c left JOIN (select classfiy_id from book) b on c.classfiy_id = b.classfiy_id GROUP BY c.classfiy_id"
        res = self.c.execute(sql)
        self.cList = res.fetchall()
        self.classfiy.clear()
        for citem in self.cList:
            item = QListWidgetItem()
            item_widget = self.get_item_wight(citem)
            self.classfiy.addItem(item)
            self.classfiy.setItemWidget(item, item_widget)
        self.classfiy.setFixedHeight(len(self.cList)*30)

    def get_item_wight(self, data):
        wight = QWidget()
        wight.setFixedHeight(30)
        item_layout = QHBoxLayout()
        item_layout.setContentsMargins(0,0,0,0)
        yuanLabel = QLabel()
        yuanLabel.setStyleSheet(f'background-color: {self.colors[int(data[2])]};')
        yuanLabel.setFixedSize(10,10)
        classfiyBtn = QPushButton(f"{data[1]} ({data[3]})")
        classfiyBtn.setProperty('class', 'cfiyBtn')
        classfiyBtn.setFixedSize(70, 25)
        classfiyBtn.clicked.connect(partial(self.checkClassfiy, data[0]))
        item_layout.addWidget(yuanLabel)
        item_layout.addWidget(classfiyBtn)
        if data[0] != 1:
            editBtn = QPushButton("...")
            editBtn.clicked.connect(partial(self.edit_classfiy,data))
        else:
            editBtn = QPushButton("")
        editBtn.setFixedSize(20, 25)
        editBtn.setStyleSheet('border:none;')
        item_layout.addWidget(editBtn)
        wight.setLayout(item_layout)
        return wight

    def checkClassfiy(self, classfiy_id):

        self.stackedWidget.setCurrentIndex(0)
        self.cid = classfiy_id
        self.init_booklist()

    def initBtn(self):
        self.cid = 0
        self.checkedList = []
        self.inBook.clicked.connect(self.open_book)
        self.inBook.setCursor(QCursor(Qt.PointingHandCursor))
        self.allBook.setCursor(QCursor(Qt.PointingHandCursor))
        self.delbookBtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.delbookBtn.clicked.connect(self.del_book)
        self.addClassfiy.clicked.connect(self.add_classfiy)
        self.addtoclassfiy.clicked.connect(partial(self.add_book_classfiy))
        self.adddelwidget.hide()
        self.aboutBtn.clicked.connect(partial(self.show_about, 0))
        self.abtn.clicked.connect(partial(self.show_about, 0))
        self.helpBtn.clicked.connect(partial(self.show_about, 1))
        self.aboutBtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.abtn.setCursor(QCursor(Qt.PointingHandCursor))
        self.helpBtn.setCursor(QCursor(Qt.PointingHandCursor))

    def show_about(self, about_index):

        self.stackedWidget.setCurrentIndex(1)
        self.textBox.setText(about_str[about_index])

    def __del__(self):
        self.close_db()

    def show_book(self, bookid):
        self.bkshow = bookShow(bookid)
        self.bkshow.show()

    def init_booklist(self):

        if self.cid == 0:
            topstr = f"全部书籍（{self.allnum}）"
        else:
            topstr = f"{self.cList[self.cid-1][1]}（{self.cList[self.cid-1][3]}）"
        self.topclassfiy.setText(topstr)

        res = self.c.execute('select * from temp where temp_name="openPath"')
        op = res.fetchall()[0]
        self.openPath = op[2]

        sql= "select * from book where 0=0"
        if self.cid != 0:
            sql += " and classfiy_id=" + str(self.cid)
        res = self.c.execute(sql)
        bookList = res.fetchall()

        row = 0
        column = 0
        grid = self.gridLayout
        if grid.count() > 0:
            for i in range(grid.count()):
                grid.itemAt(i).widget().deleteLater()
        grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        grid.setSpacing(10)
        grid.setContentsMargins(3, 0, 3, 0)
        self.booknum = len(bookList)
        self.books = []
        for i in range(len(bookList)):
            if column == 5:
                column = 0
                row += 1
            book_widget = QWidget(self)
            book_widget.setFixedSize(145,240)

            book_layout = QVBoxLayout()
            book_layout.setAlignment(Qt.AlignCenter)
            curBookid = bookList[i][0]

            lcover = myLabel()
            lcover.setProperty('class','cover')
            lcover.setFixedSize(135, 200)
            img = QPixmap(bookList[i][1])
            lcover.setPixmap(img)
            lcover.setScaledContents(True)
            lcover.setCursor(QCursor(Qt.PointingHandCursor))
            lcover.doubleclicked.connect(partial(self.show_book, curBookid))

            book_checkbox = QCheckBox(lcover)
            book_checkbox.setProperty('bookid', bookList[i][0])
            book_checkbox.setProperty('bookname', bookList[i][3])
            book_checkbox.setProperty('resid', bookList[i][2])
            book_checkbox.setProperty('logo', bookList[i][1])
            book_checkbox.hide()

            book_checkbox.stateChanged.connect(self.ckb_change)
            bckb = dict()
            bckb['obj'] = book_checkbox
            self.books.append(bckb)
            book_layout.addWidget(lcover)
            book_layout.setContentsMargins(0,0,0,0)
            ltitle = QLabel()
            ltitle.setProperty('class','title')
            ltitle.setText(bookList[i][3])
            ltitle.setFixedSize(125,30)
            ltitle.setWordWrap(True)
            ltitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            book_layout.addWidget(ltitle)
            book_widget.setLayout(book_layout)

            grid.addWidget(book_widget, row, column)
            column += 1
        self.scrollArea.widget().setLayout(grid)
        self.scrollArea.viewport().setStyleSheet("background-color:transparent;")
        vbar = self.scrollArea.verticalScrollBar()
        hbar = self.scrollArea.horizontalScrollBar()

    def del_book(self):
        if len(self.checkedList):
            i = 1
            messageStr = f"\n 是否要删除以下 {str(len(self.checkedList))} 本书籍："
            for c in self.checkedList:
                messageStr += "\n" + "(" + str(i) + ")" + "《" + c['bookname'] + "》"
                i += 1
            messageStr += "\n"
            box = self.mymessage(0, "删除书籍", messageStr)
            if box.clickedButton() == self.qyes:
                instr = "("
                for i, v in enumerate(self.checkedList):
                    instr += str(v['bookid'])
                    if i != (len(self.checkedList) - 1):
                        instr += ","
                instr += ")"
                sql = f"delete from book where book_id in {instr}"
                res = self.c.execute(sql)
                sql = f"delete from chapter where book_id in {instr}"
                res = self.c.execute(sql)
                self.conn.commit()
                self.c.execute('vacuum')
                for c in self.checkedList:
                    filePath = f'./res/images/{c["resid"]}'
                    if os.path.isdir(filePath):
                        shutil.rmtree(filePath)
                    coverPath = c["logo"]
                    if coverPath != '.\\res\\icon\\logo.png':
                        if os.path.isfile(coverPath):
                            os.remove(coverPath)
                self.init_classfiylist()
                self.init_booklist()
                self.adddelwidget.hide()

    def mymessage(self, mode, title, content):

        modes = [QMessageBox.Information, QMessageBox.Warning, QMessageBox.Question]
        box = QMessageBox(modes[mode], title, content)
        self.qyes = box.addButton(self.tr("确定"), QMessageBox.YesRole)
        self.qno = box.addButton(self.tr("取消"), QMessageBox.NoRole)
        box.exec_()
        return box

    def ckb_change(self):
      # 循环所有的checkbox
        self.checkedList = []
        for ckb_item in self.books:
            if ckb_item['obj'].isChecked():
                ckb = {}
                ckb['bookid'] = ckb_item['obj'].property('bookid')
                ckb['bookname'] = ckb_item['obj'].property('bookname')
                ckb['resid'] = ckb_item['obj'].property('resid')
                ckb['logo']  = ckb_item['obj'].property('logo')
                self.checkedList.append(ckb)
        if len(self.checkedList):
            self.adddelwidget.show()
        else:
            self.adddelwidget.hide()

    def isImage(self, pathStr):

        img_type = ["jpg", "png", "jpeg", "gif"]
        file = os.path.basename(pathStr)
        ert = file.split(".")[-1]
        if (ert in img_type):
            return True
        return False

    def isHtml(self, fname):
        exts = ['.html', '.xhtml', '.htm']
        for item in exts:
            if item in fname:
                return True
        return False

    # 去#号
    def remove_jing(self, s):
        if s.find('#'):
            re_jin = re.compile("#.*")
            s = re_jin.sub('', s)
        return s

    def get_anchor(self, s):
        ac = ""
        if s.find('#'):
            ac = s.split("#")[-1]
        return ac

    def gethtml(self, str):
        s = os.path.basename(str)
        s = s[0:s.find('.html') + 5]
        return s

    def getNew(self, oldfile):
        ts = calendar.timegm(time.gmtime())
        newfile = f'.\cover\{ts}.{oldfile.split(".")[1]}'
        return newfile

    def open_book(self):
        self.stackedWidget.setCurrentIndex(0)
        if self.openPath == "":
            self.openPath = "D:\epub"
        book1 = QFileDialog().getOpenFileName(self, '选择文件', self.openPath, '*.epub')
        if book1[0] != '':
            self.openPath = os.path.dirname(book1[0])
            curtime = str(calendar.timegm(time.gmtime()))
            bookname = os.path.basename(book1[0])
            bookname = os.path.splitext(bookname)[0]
            author = "佚名"
            logo = ".\\res\\icon\\logo.png"
            imgPath = ""
            chapter_html = {}
            family = '宋体'
            fontsize = 26
            color = "#000000"
            bgcolor = "#FFFFFF"
            with ZipFile(book1[0], 'r') as zp:
                try:
                    for f in zp.namelist():
                        ex = os.path.splitext(f)[-1]
                        if ex == '.ncx':  # 获取xx.ncx文件 解析
                            ncx_str = zp.read(f).decode()
                            handler = ncxHandler()
                            sax.parseString(ncx_str, handler)
                            chapterList = handler.titleList
                            if len(handler.bookname) != 0:
                                bookname = handler.bookname
                            if len(handler.author) != 0:
                                author = handler.author
                            sql = "select count(*) from book where title=? and author = ?"
                            isat = self.c1.execute(sql, [bookname, author]).fetchone()[0]
                            if isat != 0:
                                info = f'作者为 {author} 的 {bookname} 这本书已经存在，请勿重复加入'
                                QMessageBox.warning(self, '警告', info)
                                return
                    for f in zp.namelist():
                        if self.isHtml(f):  # 解析.html文件
                            bsf = os.path.basename(f)
                            chapter_html[bsf] = zp.read(f).decode()

                        elif (f.find('cover.') != -1):
                            ext = os.path.splitext(f)[-1]
                            fbs = os.path.basename(f)
                            logo = f".\\res\\cover\\{curtime}" + ext
                            imagesPath = f".\\res\\images\\{curtime}\\"

                            img_stream = BytesIO(zp.read(f))
                            self.change_img_size(img_stream, logo)

                            if not os.path.exists(imagesPath):
                                os.mkdir(imagesPath)
                            self.change_img_size(img_stream, imagesPath + fbs)

                        elif self.isImage(f):  # 如果是图片解压到固定目录下 bookid
                            fs = zp.getinfo(f).file_size
                            if fs > 10000:
                                filedir = f'.\\res\\images\\{curtime}\\'
                                if not os.path.exists(filedir):
                                    os.mkdir(filedir)
                                fbs = os.path.basename(f)
                                new_img_path = filedir + fbs
                                img_stream = BytesIO(zp.read(f))
                                self.change_img_size(img_stream, new_img_path)

                except BadZipfile:
                    QMessageBox.information(self, '提示框', "你导入的是非标准文件！")
                    return

            for chapter in chapterList:
                chapter["anchor"] = ""
                html = chapter['html']
                if '#' in chapter['html']:
                    html = self.remove_jing(chapter['html'])
                    chapter["anchor"] = self.get_anchor(chapter['html'])
                chapter["html_str"] = chapter_html[html]

            booksql = 'INSERT INTO book(book_id, logo, resid, title, author, family, fontsize, color, bgcolor,classfiy_id,readmode) VALUES ( NULL, ?, ?, ?, ?, ?, ?, ?, ?, 1, 1)'
            self.c.execute(booksql, [logo, curtime, bookname, author, family, fontsize, color, bgcolor])
            book_id = self.c.lastrowid
            for chapter in chapterList:
                csql = 'INSERT INTO chapter(chapter_id, book_id, anchor, index_id, parent_id, title, content) VALUES (NULL, ?, ?, ?, ?, ?, ?)'
                self.c.execute(csql, [book_id, chapter["anchor"], chapter['index'], chapter['parentid'], chapter['title'], chapter["html_str"]])
            tempsql = f"update temp set temp_value='{self.openPath}'  where temp_name='openPath'"
            self.c.execute(tempsql)

            self.conn.commit()
            info = f'导入作者为 {author} 的 {bookname} 成功！'
            QMessageBox.information(self, '提示框', info)

            self.init_classfiylist()
            self.init_booklist()

    def change_img_size(self, imgPath, new_img_path):
        img = Image.open(imgPath)
        w, h = img.size[0], img.size[1]
        new_img = img
        if w > 700:
            new_w = 700
            new_h = int(new_w * h / w)
            new_img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        new_img.save(new_img_path)

    #初始化数据库  初始字体 font-size:14px; family:宋体; color:#00000;
    def init_db(self):
        ##初始化数据库
        if os.path.isfile('./db/booklib.db') == False:
            if os.path.isdir("./db") == False:
                os.mkdir("./db")
            self.conn = sqlite3.connect('./db/booklib.db')
            self.c = self.conn.cursor()
            self.c1 = self.conn.cursor()
            self.c.execute('''CREATE TABLE if not exists book( 
                   book_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                   logo TEXT,
                   resid TEXT,
                   title TEXT,
                   author TEXT,
                   family TEXT,
                   fontsize INTEGER,
                   color TEXT,
                   bgcolor TEXT,
                   classfiy_id INTEGER,
                   readmode INTEGER 
               );''')
            self.c.execute('''CREATE TABLE if not exists chapter(
                   chapter_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                   book_id INTEGER NOT NULL,
                   anchor TEXT,
                   index_id int,
                   parent_id int,
                   title TEXT ,
                   content TEXT );
            ''')
            self.c.execute('''CREATE TABLE if not exists temp(
                   temp_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                   temp_name TEXT,
                   temp_value TEXT);
            ''')
            self.c.execute('''
            INSERT INTO temp(temp_id, temp_name, temp_value) VALUES (NULL, "openPath", "C:")
            ''')

            self.c.execute('''CREATE TABLE if not exists classfiy(
                   classfiy_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                   classfiy_name TEXT,
                   classfiy_color TEXT)
            ''')
            self.c.execute('''
                   INSERT INTO classfiy(classfiy_id, classfiy_name, classfiy_color) VALUES (NULL, "未分类", 0)
                   ''')
            self.conn.commit()
        else:
            self.conn = sqlite3.connect('./db/booklib.db')
            self.c = self.conn.cursor()
            self.c1 = self.conn.cursor()

    def close_db(self):
        self.c1.close()
        self.c.close()
        self.conn.close()

if __name__ == '__main__':

    QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    index = index()
    styleFile = './res/qss/style.qss'
    qssStyle = CommonHelper.readQss(styleFile)
    index.setStyleSheet(qssStyle)
    sys.exit(app.exec())
