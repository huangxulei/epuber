# epuber
1、本软件用于打开Epub文件的电子书阅读器。<br/>
   程序名：橘猫读书 <br/>
   操作视频：https://www.bilibili.com/video/BV1De4y1u7tW/?vd_source=cecf305399cdec49dcef2f44e80d066b <br/>
   编译后成品： 链接：https://pan.baidu.com/s/16PMGwP_w_OSrk-hlG3n95A <br/>
               提取码：8e7m <br/>
   大概：32M。 <br/>
   

2、开发相关<br/>

   开发工具：pycharm <br/>
   开发框架：基于python的组件pyqt5 <br/>
   数据库：sqlite3 <br/>
   开发时间：一个月。

3、开发者：赵阿贵<br/>

   联系QQ：37156760<br/>
   交流QQ群：616712461
   
4、开发思路<br/>
   
   1、用zipfile解压epub文件，把html文件内容放入数据库，图片文件解压成普通图片文件。<br/>
   2、数据库 有两个表格，一个book表，一个book所对应的内容表格章节表 chapter，章节进行了二级分类。<br/>
   3、布局两个页面，mainView，首页功能，进行导入操作，并且把导入的书籍进行展示，并进行分类处理。<br/>
      第二个页面 book，进行书籍阅读展示，可以改变颜色和字体。这里我用了QPrintPreviewWidget组件，但是唯一不足的<br/>
      的地方就是不能编辑，但是他提供好的地方是可以进行自动翻页操作。我不用去做这方面工作，鼠标滑动进行上下页滚动。<br/> 
      
5、开发阅读类产品，感觉还是用electron 比较好。后期我将花一个月时间开发一个electron的阅读器。
      
      
   
   
