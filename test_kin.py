import sys
from PyQt5.QtWidgets import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pyperclip
from PyQt5 import uic
import pymysql
import pyautogui
from selenium.webdriver.common.action_chains import ActionChains
import threading


Ui_MainWindow, QtBaseClass = uic.loadUiType('untitled_kin.ui')


class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.naverLogin.clicked.connect(self.naver_login)
        self.ui.megalogin.clicked.connect(self.login_test)
        self.ui.kinButton.clicked.connect(self.kin_run)
        self.ui.answerButton.clicked.connect(self.answer_run)
        self.ui.kinListCall.clicked.connect(self.kin_list)
        self.ui.whileTest.clicked.connect(self.thread_while_test)
        self.conn = pymysql.connect(
            host='112.170.181.184',
            user='python', password='ghkdgptjd2',
            db='python', charset='utf8'
        )
        self.curs = self.conn.cursor(pymysql.cursors.DictCursor)
        self.driver = webdriver.Chrome(r'resources/chromedriver.exe')
        self.driver.get('https://naver.com')
        self.mega_id = ""

    def login_check(self):
        if self.ui.myid.text() == "solidstar" and self.ui.mypass.text() == "rhfemsqpf2":
            # self.ui.textEdit.append("로그인OK")
            self.mega_id = self.ui.myid.text()
            self.ui.textEdit.append(self.mega_id)
            return True
        else:
            QMessageBox.about(self, "로그인오류", "아이디와 패스워드를 확인하세요")
            return False

    def login_test(self):
        # 로그인 인증처리
        if self.login_check():
            QMessageBox.about(self, "로그인성공", "로그인성공")
        else:
            return

    def fetchtest(self):
        sql = "select * from test_table"
        self.curs.execute(sql)
        result = self.curs.fetchall()
        idset = {'id': result[0]['varchar_1'], 'pw': result[0]['varchar_2']}
        return idset

    def kinfetch(self):
        sql = "select * from kin order by no desc"
        self.curs.execute(sql)
        result = self.curs.fetchall()
        kinset = {'dir': result[0]['dirid'], 'doc': result[0]['docid']}
        return kinset

    def mega_run(self):
        # self.driver = webdriver.Chrome()
        self.driver.get('http://megalabs.co.kr')
        time.sleep(1)

    def naver_login(self):

        self.fetchtest()
        self.driver.get('https://nid.naver.com/nidlogin.login')

        idset = self.fetchtest()
        naver_id = idset['id']
        naver_pass = idset['pw']

        # id, pw 입력할 곳을 찾습니다.
        tag_id = self.driver.find_element_by_name('id')
        tag_pw = self.driver.find_element_by_name('pw')
        tag_id.clear()

        # id 입력
        tag_id.click()
        pyperclip.copy(naver_id)
        tag_id.send_keys(Keys.CONTROL, 'v')

        # pw 입력
        tag_pw.click()
        pyperclip.copy(naver_pass)
        tag_pw.send_keys(Keys.CONTROL, 'v')

        # 로그인 버튼을 클릭합니다
        login_btn = self.driver.find_element_by_id('log.login')
        login_btn.click()

    def kin_run(self):
        kinset = self.kinfetch()
        kindir = kinset['dir']
        kindoc = kinset['doc']

        # 해당 지식인 글로 이동
        self.driver.get('https://kin.naver.com/qna/detail.nhn?d1id=1&dirId='+kindir+'&docId='+kindoc)

        # 답변하기 버튼 찾기 - 있을 때만 지식인 답변 적용
        answer_btn = self.driver.find_element_by_id('answerWriteButton')

        # 답변버튼 존재할때 버튼 클릭후 딜레이
        if answer_btn.is_displayed:
            answer_btn.click()
            time.sleep(1)

        # 태그 엘리먼트 기준으로 스크롤 처리 위한 전초작업
        answer_pos = self.driver.find_element_by_id('tagAreaForAnswer')

        if answer_pos.is_displayed:
            actions = ActionChains(self.driver)
            actions.move_to_element(answer_pos).perform()
            time.sleep(1)

    # noinspection PyMethodMayBeStatic
    def answer_run(self):
        # 답변 버튼을 이미지로 제공하고 해당 이미지 찾아서 아래쪽으로 클릭
        v = pyautogui.locateOnScreen("1234.png")
        # save the extension as image
        pyautogui.click(x=v[0], y=v[1]+300, clicks=1, interval=0.0, button="left")
        # 한글 처리를 위한 페이퍼클립 페이스트 적용
        pyperclip.copy('어쩌고 저쩌고 지화자')
        pyautogui.hotkey("ctrl", "v")

    def kin_list(self):
        # 로그인 인증처리
        if not self.login_check():
            return

        sql = "select * from kin"
        self.curs.execute(sql)
        rows = self.curs.fetchall()
        listtable = self.ui.kinListTable

        # 테이블 위젯에 행 적용
        listtable.setRowCount(len(rows))

        count = 0
        for row in rows:
            # 각 컬럼에 DB 값 연동처리
            listtable.setItem(count, 0, QTableWidgetItem(str(row['no'])))
            listtable.setItem(count, 1, QTableWidgetItem(row['subject']))
            listtable.setItem(count, 2, QTableWidgetItem(row['content']))
            listtable.setItem(count, 3, QTableWidgetItem(row['id']))
            listtable.setItem(count, 4, QTableWidgetItem(self.mega_id))
            count += 1

    def while_test(self):
        cnt = 0
        while True:
            cnt += 1
            # self.ui.textEdit.append(str(cnt))
            self.ui.logArea.append(str(cnt))
            time.sleep(1)
            print(cnt)
            if cnt == 10:
                break

    def thread_while_test(self):
        # t = threading.Thread(target=self.while_test, args=())
        t = threading.Thread(target=self.while_test)
        t.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
