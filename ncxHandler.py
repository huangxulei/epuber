# @Time:2022/11/15 17:12
# @Author: 赵阿贵
# @File:ncxHandler.py
from xml import sax
import os
class ncxHandler(sax.ContentHandler):
    def __init__(self):
        sax.ContentHandler.__init__(self)
        self._content = ""
        self._tag = ""
        self.bookname = "" #书名
        self.author = ""   #作者
        self.titleList = [] #列表list j {}
        self.title = ""
        self.html = ""
        self.index = 1
        self.curindex = 1
        self.parent = 1
    def startElement(self, name, attrs):
        self._tag = name
        if name == "content":
            self.html = attrs["src"]
            if  self.index ==  self.curindex:
                self.parent = self.index
                j = {}
                j['index'] = self.index
                j['parentid'] = 0
                j['title'] = self.title
                j['html'] = os.path.basename(self.html)
                self.titleList.append(j)
            else:
                j = {}
                j['index'] = self.index
                j['parentid'] = self.parent
                j['title'] = self.title
                j['html'] = os.path.basename(self.html)
                self.titleList.append(j)
        # elif name == "navMap":
        #     self.bookname = self.title

    def endElement(self, name):
        if name == "text":
            self.title = self._content
        elif name == "content":
            self.index += 1
        elif name == "navPoint":
            self.curindex += 1
        elif name == "docTitle":
            self.bookname = self.title
        elif name == "docAuthor":
            self.author = self.title
    def characters(self, content):
        self._content = content

    # def gethtml(self, str):
    #     s = os.path.basename(str)
    #     s = s[0:s.find('html') + 4]
    #     return s

if __name__ == '__main__':

    handler = ncxHandler()
    sax.parse("fb.ncx", handler)