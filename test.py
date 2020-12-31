import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pyperclip
import pymysql


Ui_MainWindow, QtBaseClass = uic.loadUiType(r'resources\untitled.ui')


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.btn_clicked)
        self.ui.mega.clicked.connect(self.mega_clicked)
        self.conn = pymysql.connect(
            host='112.170.181.184',
            user='python', password='ghkdgptjd2',
            db='python', charset='utf8'
        )
        self.curs = self.conn.cursor(pymysql.cursors.DictCursor)
        self.driver = webdriver.Chrome(r'resources\chromedriver.exe')

    def btn_clicked(self):
        # print_hi('HelloPyCharm')
        # self.ui.textEdit.setText("Hello World!")
        self.naver_run()

    def mega_clicked(self):
        # print_hi('HelloPyCharm')
        # self.ui.textEdit.setText("Hello World!")
        self.kin_run()

    def fetchtest(self):
        sql = "select * from test_table"
        self.curs.execute(sql)
        result = self.curs.fetchall()
        self.ui.textEdit.append(result[0]['varchar_1'])
        idset = {'id': result[0]['varchar_1'], 'pw': result[0]['varchar_2']}
        return idset

    def kin_run(self):
        # self.driver = webdriver.Chrome()
        self.driver.get('http://megalabs.co.kr')
        time.sleep(1)

    def naver_run(self):
        self.fetchtest()
        # self.driver = webdriver.Chrome()
        self.driver.get('https://nid.naver.com/nidlogin.login')
        time.sleep(1)

        '''
        naver_id = self.ui.myid.text()
        self.ui.textEdit.append("아이디입력\n")
        naver_pass = self.ui.mypass.text()
        self.ui.textEdit.append("비번입력\n")
        '''
        idset = self.fetchtest()
        naver_id = idset['id']
        naver_pass = idset['pw']

        # 로그인 버튼을 찾고 클릭합니다
        # login_btn = driver.find_element_by_class_name('ico_local_login')
        # login_btn.click()
        # time.sleep(1)

        # id, pw 입력할 곳을 찾습니다.
        tag_id = self.driver.find_element_by_name('id')
        tag_pw = self.driver.find_element_by_name('pw')
        tag_id.clear()
        time.sleep(1)

        # id 입력
        tag_id.click()
        pyperclip.copy(naver_id)
        tag_id.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)

        # pw 입력
        tag_pw.click()
        pyperclip.copy(naver_pass)
        tag_pw.send_keys(Keys.CONTROL, 'v')
        time.sleep(1)

        # 로그인 버튼을 클릭합니다
        login_btn = self.driver.find_element_by_id('log.login')
        login_btn.click()
        # sys.exit(app.exec_())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()

    # btnRun = ui.run
    # btnRun.clicked.connect(naver_run)


# sys.exit(app.exec_())
