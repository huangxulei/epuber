# @Time:2022/12/1 23:54
# @Author: 赵阿贵
# @File:classfiy_dialog.py
from PyQt5.QtWidgets import QDialog, QPushButton , QLineEdit, QHBoxLayout, QVBoxLayout, QMessageBox, QButtonGroup, QRadioButton, QWidget, QSpacerItem, QComboBox ,QLabel
from PyQt5.QtCore import Qt
from functools import partial


class AddDialog(QDialog):

    def __init__(self, parent=None):
        super(AddDialog, self).__init__(parent)
        self.colors = ['gray', 'black', 'red', 'blue', 'green', 'orange']
        self.init_ui(parent)
        self.setWindowTitle("添加分类")

    def init_ui(self, parent):
        '''水平布局'''
        vbox = QVBoxLayout()
        self.name_text = QLineEdit()
        self.name_text.setFixedSize(170,30)
        self.name_text.setPlaceholderText('请输入分类名称')

        self.save_btn = QPushButton()
        self.save_btn.setText('保存')
        self.save_btn.setFixedSize(50,30)
        self.save_btn.clicked.connect(lambda: self.save_btn_click(parent))


        color_layout = QHBoxLayout()

        self.colorbtns = QButtonGroup()
        for index, value in enumerate(self.colors):
            rbtn = QRadioButton()
            rbtn.setStyleSheet(f"background-color: {value}; ")
            if index == 0:
                rbtn.setChecked(True)
            self.colorbtns.addButton(rbtn, index)
            color_layout.addWidget(rbtn)

        color_layout.addSpacerItem(QSpacerItem(20, 30))
        vbox.addWidget(self.name_text)
        vbox.addLayout(color_layout)
        vbox.addWidget(self.save_btn)

        self.setLayout(vbox)

    def save_btn_click(self, parent):
        if self.name_text.text().strip():
            data = [self.name_text.text(), self.colorbtns.checkedId()]
            parent.save_classfiy(data)
            self.close()
        else:
            QMessageBox.warning(self, "警告", "分类名称不能为空！")

    def cancel_btn_click(self):
        self.close()

    @staticmethod
    def get_add_dialog(parent=None):
        dialog = AddDialog(parent)
        return dialog.exec()

class EditDialog(QDialog):

    def __init__(self, cdata , parent=None):
        super(EditDialog, self).__init__(parent)
        self.colors = ['gray', 'black', 'red', 'blue', 'green', 'orange']
        self.cdata = cdata
        self.init_ui(cdata, parent)
        self.setWindowTitle("编辑分类")

    def init_ui(self, cdata, parent):

        vbox = QVBoxLayout()
        self.name_text = QLineEdit()
        self.name_text.setFixedSize(170,30)
        self.name_text.setText(self.cdata[1])

        hbox = QHBoxLayout()

        self.edit_btn = QPushButton()
        self.edit_btn.setText('修改')
        self.edit_btn.setFixedSize(50,30)

        self.del_btn = QPushButton()
        self.del_btn.setText('删除')
        self.del_btn.setFixedSize(50,30)

        hbox.addWidget(self.edit_btn)
        hbox.addWidget(self.del_btn)

        color_layout = QHBoxLayout()

        self.colorbtns = QButtonGroup()
        for index, value in enumerate(self.colors):
            rbtn = QRadioButton()
            rbtn.setStyleSheet(f"background-color: {value}; ")
            if index == int(self.cdata[2]):
                rbtn.setChecked(True)
            self.colorbtns.addButton(rbtn, index)
            color_layout.addWidget(rbtn)

        color_layout.addSpacerItem(QSpacerItem(20, 30))
        vbox.addWidget(self.name_text)
        vbox.addLayout(color_layout)
        vbox.addLayout(hbox)

        self.edit_btn.clicked.connect(partial(self.edit_btn_click, parent))
        self.del_btn.clicked.connect(partial(self.del_btn_click, parent))

        self.setLayout(vbox)

    def edit_btn_click(self, parent):
        if self.name_text.text().strip():
            edata = [self.cdata[0], self.name_text.text(), self.colorbtns.checkedId()]
            parent.save_classfiy_db(edata)
            self.close()
        else:
            QMessageBox.warning(self, "警告", "分类名称不能为空！")

    def del_btn_click(self, parent):

        parent.del_classfiy(self.cdata)
        self.close()

    @staticmethod
    def get_edit_dialog(cdata, parent=None):
        dialog = EditDialog(cdata, parent)
        return dialog.exec()

class AddBookClassfiy(QDialog):

    def __init__(self, classList, parent=None):

        super(AddBookClassfiy, self).__init__(parent)
        self.classList = classList
        self.init_ui(parent)
        self.setWindowTitle("添加到分类")

    def init_ui(self, parent):

        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        cl = QLabel("分类名称：")
        self.cb = QComboBox()
        for c in self.classList:
            self.cb.addItem(c[1])
        hbox1.addWidget(cl)
        hbox1.addWidget(self.cb)

        self.add_btn = QPushButton()
        self.add_btn.setText('添加')
        self.add_btn.setFixedSize(50, 30)

        self.add_btn.clicked.connect(partial(self.add_btn_click, parent))
        vbox.addLayout(hbox1)
        vbox.addWidget(self.add_btn)
        self.setLayout(vbox)

    def add_btn_click(self, parent):

        parent.add_book_classfiy_db(self.cb.currentIndex())
        self.close()

    @staticmethod
    def get_add_dialog(classList, parent=None):
        dialog = AddBookClassfiy(classList, parent)
        return dialog.exec()
