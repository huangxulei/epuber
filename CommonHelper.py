# @Time:2022/11/10 19:34
# @Author: 赵阿贵
# @File:CommonHelper.py

class CommonHelper:
    @staticmethod
    def readQss(style):
        with open(style,'r') as f:
            return f.read()

