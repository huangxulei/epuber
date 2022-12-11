# @Time:2022/11/12 10:01
# @Author: 赵阿贵
# @File:bookShow.py
import sqlite3
from PyQt5.QtWidgets import QWidget, QApplication, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QColorDialog, QFontDialog,QLabel, QPushButton, QMainWindow,QSpacerItem,QHeaderView, QTextBrowser, QGraphicsItem, QGraphicsPixmapItem, QGraphicsScene, QGraphicsView
from PyQt5.QtCore import Qt, pyqtSignal, QSizeF
from PyQt5.QtGui import QFont, QColor, QFontMetrics, QPageSize, QCursor, QTextDocument, QTextCursor, QGuiApplication
from PyQt5.QtPrintSupport import QPrintPreviewWidget, QPrinter
import sys
from book import Ui_MainWindow
import os, re
from functools import partial

class myLabel(QLabel):
    clicked = pyqtSignal()
    def mouseReleaseEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton:
            self.clicked.emit()
    def enterEvent(self, QMouseEvent): #移入控件事件
        self.setCursor(Qt.PointingHandCursor)

class bookShow(QMainWindow, Ui_MainWindow):
    my_singal = pyqtSignal(object)

    def onClicked(self, item):
        index = item.data(0, Qt.ItemDataRole.UserRole)
        anchor = item.data(0, Qt.ItemDataRole.UserRole+1)
        # print("anchor:"+anchor)
        curChapter = self.chapterList[index-1]
        self.html_str = self.parse_img(curChapter[4])
        self.update_html(1)

    def update_html(self, cur):

        self.html_str = self.parse_img(self.html_str)
        self.textBrowser.setHtml(self.html_str)
        self.preview.updatePreview()
        if cur !=0:
            self.preview.setCurrentPage(cur)

    def __init__(self, bookid):

        super(bookShow, self).__init__()
        self.setupUi(self)
        self.readmodetext = ['单页','两页']
        self.bookid = bookid
        self.ffont = QFont()
        self.ffont.setPointSize(14)
        self.ffont.setBold(True)
        tree = self.chapterTree
        tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        tree.setStyleSheet('''
            font-size:13px;
        ''')
        bar = tree.verticalScrollBar()
        bar.setStyleSheet('''
        QScrollBar{  
            background:transparent; 
            width:8px;
            background-color: gray;
        }
        ''')
        # 1、初始化
        self.chapterList = self.getBookid(self.bookid)
        self.setWindowTitle(self.bookname)
        for chapter0 in self.getByParent(0):
            item0 = QTreeWidgetItem(tree)
            item0.setText(0, chapter0[3])
            item0.setData(0, Qt.ItemDataRole.UserRole, chapter0[1])
            item0.setData(0, Qt.ItemDataRole.UserRole+1, chapter0[0])
            item0.setToolTip(0,chapter0[3])
            for chapter1 in self.getByParent(chapter0[1]):
                item1 = QTreeWidgetItem(item0)
                item1.setText(0, chapter1[3])
                item1.setData(0, Qt.ItemDataRole.UserRole, chapter1[1])
                item1.setData(0, Qt.ItemDataRole.UserRole + 1, chapter1[0])
                item1.setToolTip(0, chapter1[3])
        tree.itemClicked['QTreeWidgetItem*', 'int'].connect(self.onClicked)

        c0 = self.chapterList[0]
        self.html_str = self.parse_img(c0[3])

        self.textBrowser = QTextBrowser()
        self.textBrowser.setHtml(self.html_str)
        self.preview = QPrintPreviewWidget(self.contentFrame)
        self.preview.setContentsMargins(0, 0, 0, 0)
        # self.preview.setStyleSheet(f'''
        #     QGraphicsView {{
        #         qproperty-backgroundBrush: {self.bgcolor} ;
        #     }}
        #     ''')
        self.preview.setViewMode(self.readmode)
        self.preview.setFixedSize(1300, 900)
        self.preview.paintRequested.connect(self.print_preview)
        qgview = self.preview.findChild(QGraphicsView)
        if qgview:
            qgview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            qgview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.resize(1300, 900)

        # self.textBrowser.setText(self.html_str)
        lfont = QFont()
        lfont.setPointSize(11)

        self.openBtn = QPushButton("展开")
        self.openBtn.setFixedSize(60,28)
        self.closeBtn = QPushButton("收缩")
        self.closeBtn.setFixedSize(60,28)
        self.openBtn.setFont(lfont)
        self.closeBtn.setFont(lfont)
        self.treeTopLayout.addWidget(self.openBtn)
        self.treeTopLayout.addSpacerItem(QSpacerItem(5,5))
        self.treeTopLayout.addWidget(self.closeBtn)
        self.treeTopLayout.setAlignment(Qt.AlignLeft)

        self.openBtn.clicked.connect(partial(self.open_close, True))
        self.closeBtn.clicked.connect(partial(self.open_close, False))

        self.fontLabel = myLabel()
        self.fontLabel.setFixedSize(280, 20)
        self.fontLayout.addWidget(self.fontLabel)
        self.fontLabel.clicked.connect(self.change_font)

        self.colorText = QLabel()
        self.colorText.setFixedSize(50, 20)
        self.colorText.setText("颜色")
        self.colorText.setFont(self.ffont)

        self.colorLabel = myLabel()
        self.colorLabel.setFixedSize(25, 20)
        self.colorLabel.setStyleSheet('border:none; ')

        self.bgcolorText = QLabel()
        self.bgcolorText.setFixedSize(70, 20)
        self.bgcolorText.setText(" 背景色")
        self.bgcolorText.setFont(self.ffont)

        self.bgcolorLabel = myLabel()
        self.bgcolorLabel.setFixedSize(20, 20)
        self.bgcolorLabel.setStyleSheet('border:none; ')

        self.paperText = QLabel()
        self.paperText.setFixedSize(100, 20)
        self.paperText.setText(" 阅读模式：")
        self.paperText.setFont(self.ffont)

        self.paperLabel = myLabel()
        self.paperLabel.setFixedSize(40, 20)
        self.paperLabel.setStyleSheet('border:none; ')
        print(self.readmode)
        self.paperLabel.setText(self.readmodetext[self.readmode])
        self.paperLabel.setFont(self.ffont)

        self.fontLayout.addWidget(self.colorText)
        self.fontLayout.addWidget(self.colorLabel)
        self.fontLayout.addWidget(self.bgcolorText)
        self.fontLayout.addWidget(self.bgcolorLabel)
        self.fontLayout.addWidget(self.paperText)
        self.fontLayout.addWidget(self.paperLabel)
        self.fontLayout.setAlignment(Qt.AlignLeft)
        self.fontLayout.setContentsMargins(0,0,0,0)
        self.colorLabel.clicked.connect(self.getColor)
        self.bgcolorLabel.clicked.connect(self.getbgColor)
        self.paperLabel.clicked.connect(self.changeread)

        self.show()
        # 2、样式初始化
        self.init_style()

    def changeread(self):

        if self.readmode == 1:
            self.readmode = 0
        else:
            self.readmode = 1
        ssql = f"update book set readmode=? where book_id={self.bookid}"
        self.cc.execute(ssql, [self.readmode])
        self.connc.commit()
        self.preview.setViewMode(self.readmode)
        self.update_html(0)
        self.paperLabel.setText(self.readmodetext[self.readmode])


    def print_preview(self, printer):

        # self.textBrowser.document().setPageSize(QSizeF(printer.width(), printer.height()))
        self.textBrowser.print(printer)

    def open_close(self, isno):
        if isno:
            self.chapterTree.expandAll()
        else:
            self.chapterTree.collapseAll()

    def init_style(self):
        #初始化字体和颜色
        cFont = QFont()
        cFont.setFamily(self.family)
        cFont.setPointSize(self.fontsize)
        self.textBrowser.setStyleSheet(f'color: {self.color}; background-color: {self.bgcolor}')

        self.colorLabel.setStyleSheet(f'background-color: {self.color}')
        self.bgcolorLabel.setStyleSheet(f'background-color: {self.bgcolor}')
        self.textBrowser.setFont(cFont)

        self.fontLabel.setText(self.font_str(cFont))
        self.fontLabel.setFont(self.ffont)

        bbar = self.textBrowser.verticalScrollBar()
        bbar.setStyleSheet('''
            QScrollBar{  
                background:transparent; 
                width:8px;
                background-color: gray;
            }
        ''')

    def font_str(self, qfont):
        qf_str = f'字体：{qfont.family()} 大小：{qfont.pointSize()}'
        return qf_str

    def getColor(self):
        color = QColorDialog.getColor(QColor(self.color))
        if color.isValid():
            bgc = f'background-color: {color.name()}'
            self.colorLabel.setStyleSheet(bgc)
            # textcolor = f'color: {color.name()}'
            colors = f'''
                background-color: {self.bgcolor};
                color:{color.name()}
            '''
            # self.textBrowser.setStyleSheet(colors)
            self.preview.setStyleSheet(colors)
            self.save_color(color)
            self.color = color.name()
            self.update_html(0)

    def getbgColor(self):
        color = QColorDialog.getColor(QColor(self.bgcolor))
        if color.isValid():
            bgc = f'background-color: {color.name()}'
            self.bgcolorLabel.setStyleSheet(bgc)
            colors = f'''
                background-color: {color.name()};
                color:{self.color}
            '''
            self.save_bgcolor(color)
            self.bgcolor = color.name()
            self.update_html(0)

    def save_bgcolor(self,color):
        ssql = f"update book set bgcolor=? where book_id={self.bookid}"
        self.cc.execute(ssql, [color.name()])
        self.connc.commit()

    def save_color(self,color):
        ssql = f"update book set color=? where book_id={self.bookid}"
        self.cc.execute(ssql, [color.name()])
        self.connc.commit()

    def change_font(self):
        (font, ok) = QFontDialog.getFont(self.textBrowser.font(), self, "字体/大小设置")
        if font:
            self.textBrowser.setFont(font)
            self.fontLabel.setText(self.font_str(font))
            self.save_font(font)
            self.family = font.family()
            self.fontsize = font.pointSize()
            # self.html_str = self.parse_img(self.html_str)
            # self.textBrowser.setHtml(self.html_str)
            self.html_str = self.parse_img(self.html_str)
            self.preview.updatePreview()

    def save_font(self, qfont):
        ssql = f"update book set family=?, fontsize=? where book_id={self.bookid}"
        self.cc.execute(ssql,[qfont.family(), qfont.pointSize()])
        self.connc.commit()


    def renderHtml(self, html_str):
        #<img
        image_str = f"./res/images/{self.resid}"
        html_str = html_str.replace("images", image_str)
        # html_str = self.parse_css(html_str)
        return html_str

    def parse_img(self, html_str):

        #获取字体宽度
        fw = QFontMetrics(QFont(self.family,self.fontsize))
        fs2 = fw.width("缩进")
        css_str = f'''
            </head>
            <style>
              h3,h4 {{text-align: center;}}
              p{{ text-indent: {fs2}px;}}
              body{{color:{self.color}; background-color:{self.bgcolor};}}
            </style>
        '''
        re_css = re.compile("</head>")
        html_str = re_css.sub(css_str, html_str)

        re_link = re.compile('(<link.*?/>)')
        html_str = re_link.sub('', html_str)

        re_class = re.compile('(class=".*?")')
        html_str = re_class.sub('', html_str)

        re_n = re.compile("^[\n]")
        html_str = re_n.sub('', html_str)

        re_img = re.findall('<img.*?src="(.*?)"', html_str)
        if re_img:
            for img in re_img:
                bsf = os.path.basename(img)
                new_img = f"./res/images/{self.resid}/{bsf}"
                # new_img = new_img + '"' +' width="800" height="600'
                html_str = html_str.replace(img, new_img)
        return html_str

    def add_css(self, html_str):

        re_h3 = re.compile("^[\n]")

    # 1、获取数据库信息 书的信息 字体  大小 颜色
    def getBookid(self, bookid):
        self.bookid = bookid
        chapterList = []
        self.connc = sqlite3.connect('./db/booklib.db')
        self.cc = self.connc.cursor()
        bsql = f"select * from book where book_id= {bookid}"
        res = self.cc.execute(bsql)
        resbook = res.fetchall()[0]
        self.bookname = resbook[3]
        self.resid = resbook[2]
        self.family = resbook[5]
        self.fontsize = resbook[6]
        self.color = resbook[7]
        self.bgcolor = resbook[8]
        self.readmode = resbook[10]
        csql = f"select anchor,index_id,parent_id,title,content from chapter where book_id= {bookid}"
        res = self.cc.execute(csql)
        chapterList = res.fetchall()
        self.connc.commit()
        return chapterList

    # 给一个parentid，获取父节点 parentid 的所有子节点
    def getByParent(self, parentid):
        templist = []
        for item in self.chapterList:
            if item[2] == parentid:
                templist.append(item)
        return templist

    def __del__(self):

        self.cc.close()
        self.connc.close()


if __name__ == '__main__':
    
    QGuiApplication.setAttribute(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    bs = bookShow()
    sys.exit(app.exec())





