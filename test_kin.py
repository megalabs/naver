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
from selenium.webdriver.common.alert import Alert


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
        self.ui.whileCheck.clicked.connect(self.thread_while_test)
        self.ui.answerUpdate.clicked.connect(self.answer_input)
        self.ui.answerListCall.clicked.connect(self.answer_list)
        self.conn = pymysql.connect(
            host='112.170.181.184',
            user='kin', password='ghkdgptjd2',
            db='kin', charset='utf8'
        )
        self.curs = self.conn.cursor(pymysql.cursors.DictCursor)
        self.driver = webdriver.Chrome(r'resources/chromedriver.exe')
        self.driver.get('https://naver.com')
        self.mega_id = ""
        self.mega_keyword = "실업급여"

    def login_check(self):
        if self.ui.myid.text() == "solidstar" and self.ui.mypass.text() == "rhfemsqpf2":
            self.mega_id = self.ui.myid.text()
            self.ui.logArea.append(self.mega_id)
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
        """
        sql = "select * from test_table"
        self.curs.execute(sql)
        result = self.curs.fetchall()
        """
        #idset = {'id': result[0]['varchar_1'], 'pw': result[0]['varchar_2']}
        idset = {'id': "neoalba", 'pw': "ghkdgptjd2"}
        return idset

    def kinfetch(self):
        sql = "select * from kin where status = 0 and keyword = '"+ self.mega_keyword +"' order by no desc limit 1"
        self.curs.execute(sql)
        result = self.curs.fetchall()
        kinset = {'no':result[0]['no'], 'dir': result[0]['dirid'], 'doc': result[0]['docid']}
        return kinset

    def mega_run(self):
        # self.driver = webdriver.Chrome()
        self.driver.get('http://megalabs.co.kr')
        time.sleep(1)

    def naver_login(self):

        self.fetchtest()
        self.driver.get('https://nid.naver.com/nidlogin.login')
        self.ui.logArea.append("로그인창 로딩")

        idset = self.fetchtest()
        naver_id = idset['id']
        naver_pass = idset['pw']
        self.ui.logArea.append("아이디추출중 1단계")

        # id, pw 입력할 곳을 찾습니다.
        tag_id = self.driver.find_element_by_name('id')
        tag_pw = self.driver.find_element_by_name('pw')
        tag_id.clear()

        # id 입력
        tag_id.click()
        pyperclip.copy(naver_id)
        tag_id.send_keys(Keys.CONTROL, 'v')
        self.ui.logArea.append("아이디입력")
        time.sleep(1)

        # pw 입력
        tag_pw.click()
        pyperclip.copy(naver_pass)
        tag_pw.send_keys(Keys.CONTROL, 'v')
        self.ui.logArea.append("패스워드입력")
        time.sleep(1)

        # 로그인 버튼을 클릭합니다
        login_btn = self.driver.find_element_by_id('log.login')
        login_btn.click()
        self.ui.logArea.append("로그인버튼 클릭")
        time.sleep(1)

    def kin_run(self):

        try:
            da = Alert(self.driver)
            da.accept()
        except:
            pass

        kinset = self.kinfetch()
        kindir = kinset['dir']
        kindoc = kinset['doc']
        kinno = kinset['no']

        # 해당 지식인 글로 이동
        self.driver.get('https://kin.naver.com/qna/detail.nhn?d1id=1&dirId='+kindir+'&docId='+kindoc)

        time.sleep(1)

        # 답변하기 버튼 찾기 - 있을 때만 지식인 답변 적용
        try:
            answer_btn = self.driver.find_element_by_id('answerWriteButton')
        except:
            sql = "update kin set status = '2' where no = '" + str(kinno) + "'"
            self.curs.execute(sql)
            return

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

        # 답변하기 이전에 미리 업데이트 시켜놓아야 문제가 안생길듯 아래쪽은 브레이크 포인트가 있어서
        sql = "update kin set status = '1' where no = '" + str(kinno) + "'"
        self.curs.execute(sql)

        # 답변하기
        self.answer_run()

    # noinspection PyMethodMayBeStatic
    def answer_run(self):
        # 답변 버튼을 이미지로 제공하고 해당 이미지 찾아서 아래쪽으로 클릭
        v = pyautogui.locateOnScreen("1234.png")
        # save the extension as image
        pyautogui.click(x=v[0], y=v[1]+300, clicks=1, interval=0.0, button="left")
        # 한글 처리를 위한 페이퍼클립 페이스트 적용
        pyperclip.copy('어쩌고 저쩌고 지화자')
        pyautogui.hotkey("ctrl", "v")
        time.sleep(1)
        pyautogui.click(x=v[0]+20, y=v[1]+20, clicks=1, interval=0.0, button="left")

        time.sleep(2)
        while True:
            try:
                captcha = self.driver.find_element_by_id('au_captcha')
            except:
                break

            if captcha.is_displayed:
                time.sleep(1)
                continue
            else:
                break


    def kin_list(self):
        # 로그인 인증처리
        if not self.login_check():
            return

        sql = "select * from kin where status = 0 and keyword = '"+self.mega_keyword+"' order by no desc"
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

    def answer_list(self):
        # 로그인 인증처리
        if not self.login_check():
            return

        keyword = self.ui.keyword.text()

        sql = "select * from kin_answer where keyword = '"+keyword+"' order by no desc"
        self.curs.execute(sql)
        rows = self.curs.fetchall()
        listtable = self.ui.answerListTable

        # 테이블 위젯에 행 적용
        listtable.setRowCount(len(rows))

        count = 0
        for row in rows:
            # 각 컬럼에 DB 값 연동처리
            listtable.setItem(count, 0, QTableWidgetItem(row['keyword']))
            listtable.setItem(count, 1, QTableWidgetItem(row['content']))

            count += 1

    def answer_input(self):
        # title = self.ui.ansTitle
        content = self.ui.ansText.toPlainText()
        keyword = self.ui.keyword.text()

        sql = "insert into kin_answer (no, member_id, keyword, content) values ( null, 'solidstar', '"+keyword+"', '"+content+"') "
        try:
            self.ui.logArea.append(sql)
            self.curs.execute(sql)
            return
        except Exception as e:
            print(e)

    def while_test(self, totalcnt):
        cnt = 0
        self.ui.whileCheck.setChecked(True)
        self.ui.whileCheck.setText("중지")
        while True:
            cnt += 1

            self.ui.progressBar.setValue(cnt)
            if not self.ui.whileCheck.isChecked():
                self.ui.whileCheck.setText("시작")
                break

            self.kin_run()
            self.ui.logArea.append(str(cnt))
            time.sleep(1)

            # 최대값 도달시 종료되게 처리
            if cnt == totalcnt:
                self.ui.whileCheck.setChecked(False)
                self.ui.whileCheck.setText("시작")
                self.ui.logArea.append("최대값 도달 종료")
                break

    def thread_while_test(self):
        # 테스트용 쿼리
        # sql = "update kin set status = '0' where keyword = '실업급여' order by no desc limit 32"
        # self.curs.execute(sql)


        # 전체 갯수 뽑아내서 맥스값 변경후 처리
        sql = "select count(*) as cnt from kin where status = 0 and keyword = '"+self.mega_keyword+"'"
        self.curs.execute(sql)
        result = self.curs.fetchone()
        totalcnt = result['cnt']
        self.ui.logArea.append("전체 갯수 : " + str(totalcnt))
        self.ui.progressBar.setMaximum(totalcnt)


        if self.ui.whileCheck.isChecked():
            # t = threading.Thread(target=self.while_test, args=())
            # 인자 하나 전달할때 리스트형 변수가 아니면 저렇게 콤마 찍어야 한다네
            t = threading.Thread(target=self.while_test, args=(totalcnt,))
            t.start()


        else:
            self.ui.whileCheck.setText("시작")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
