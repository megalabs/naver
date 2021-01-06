import sys
from PyQt5.QtWidgets import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pyperclip
from PyQt5 import uic
import pymysql
from selenium.webdriver.common.action_chains import ActionChains
import threading

# 리캡차 처리를 위한 임포트 모듈 모음
import os
from PIL import Image
import requests
from io import BytesIO
from twocaptcha import TwoCaptcha
from selenium.webdriver.common.alert import Alert

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

Ui_MainWindow, QtBaseClass = uic.loadUiType('untitled_kin_jjr.ui')


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
        self.ui.answerDelete.clicked.connect(self.answer_delete)

        self.ui.naverTest.clicked.connect(self.naver_write_test)

        self.ui.answerListTable.cellClicked.connect(self.answer_clicked)
        self.ui.keywordList.currentIndexChanged.connect(self.keyword_changed)

        # frame 추가해서 지식인리스트 클릭하면 새창에서 수정할 수 있도록 추가 JJR 2021-01-05
        self.answer_frame_hide()
        self.ui.answerFrameClose.clicked.connect(self.answer_frame_hide)
        self.ui.answerwriteBtn.clicked.connect(self.answer_input_form)

        self.conn = pymysql.connect(
            host='112.170.181.184',
            user='kin', password='ghkdgptjd2',
            db='kin', charset='utf8'
        )
        self.curs = self.conn.cursor(pymysql.cursors.DictCursor)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("start-maximised")

        # self.driver = webdriver.Chrome(r'resources/chromedriver.exe', chrome_options=chrome_options)
        self.driver = webdriver.Chrome(r'resources/chromedriver.exe')
        self.driver.implicitly_wait(time_to_wait=5)

        # 처음에 빈화면인거 걸려서 그냥 넣음
        self.driver.get('https://naver.com')
        self.driver.implicitly_wait(3)
        # driver.get_screenshot_as_file('naver_main_headless.png')

        self.mega_id = ""

        # DB에서 뽑아오는걸로 수정 JJR 2021-01-05
        # self.mykeyword = ["요", "실업급여", "이혼", "홈페이지제작"]
        # self.mega_keyword = "요"
        self.mega_keyword = ""
        self.init_keyword()

    def get_captcha(self):
        iscap = self.driver.find_element_by_css_selector('.popup__captcha_image img').get_attribute('src')
        return iscap

    def init_keyword(self):
        # DB에서 뽑아오는걸로 수정 JJR 2021-01-05
        sql = "select distinct(keyword) from kin_answer where member_id='" + self.mega_id + "'"
        self.curs.execute(sql)
        result = self.curs.fetchall()
        keyword = self.mega_keyword

        # 키워드가 작동중에 바뀌면 새로 불러오려고 clear 시킴 JJR 2021-01-05
        self.ui.keywordList.clear()
        self.ui.keywordList.addItem("")
        for key in result:
            self.ui.keywordList.addItem(key['keyword'])

        self.ui.keywordList.setCurrentText(keyword)

    def keyword_changed(self):
        self.mega_keyword = self.ui.keywordList.currentText()
        # 키워드 바뀔 때 바로바로 리스트 호출 JJR 2021-01-06
        self.answer_list()

    def login_check(self):
        # 디비에서 가지고 오도록 처리 JJR 2021-01-06
        sql = "select member_pw from kin_member where member_id='" + self.ui.myid.text() + "'"
        self.curs.execute(sql)
        result = self.curs.fetchone()

        if self.ui.mypass.text() == result['member_pw']:
            self.mega_id = self.ui.myid.text()
            self.ui.logArea.append(self.mega_id)
            self.init_keyword()

            return True
        else:
            QMessageBox.about(self, "로그인오류", "아이디와 패스워드를 확인하세요")
            return False

        # if self.ui.myid.text() == "solidstar" and self.ui.mypass.text() == "rhfemsqpf2":
        #     self.mega_id = self.ui.myid.text()
        #     self.ui.logArea.append(self.mega_id)
        #     return True
        # else:
        #     QMessageBox.about(self, "로그인오류", "아이디와 패스워드를 확인하세요")
        #     return False

    def login_test(self):
        # 로그인 인증처리
        if self.login_check():
            QMessageBox.about(self, "로그인성공", "로그인성공")
            self.ui.loginFrame.hide()

        else:
            return

    # 네이버 아이디 가져오기 모듈명도 바꿔야함
    def get_naver_account(self):
        """
        sql = "select * from test_table"
        self.curs.execute(sql)
        result = self.curs.fetchall()
        """
        # idset = {'id': result[0]['varchar_1'], 'pw': result[0]['varchar_2']}
        idset = {'id': "gkrzus31542", 'pw': "aprkaprk!#%&("}
        return idset

    # 아이디도 조건절에 추가 되어야함
    def kinfetch(self):
        sql = "select * from kin where status = 0 and keyword = '" + self.mega_keyword + "' order by no desc limit 1"
        self.curs.execute(sql)
        result = self.curs.fetchall()
        kinset = {'no': result[0]['no'], 'dir': result[0]['dirid'], 'doc': result[0]['docid']}
        return kinset

    def naver_login(self):

        self.driver.get('https://nid.naver.com/nidlogin.login')
        self.ui.logArea.append("로그인창 로딩")

        idset = self.get_naver_account()
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

        kinset = self.kinfetch()
        kindir = kinset['dir']
        kindoc = kinset['doc']
        kinno = kinset['no']

        # 해당 지식인 글로 이동
        self.driver.get('https://kin.naver.com/qna/detail.nhn?d1id=1&dirId=' + kindir + '&docId=' + kindoc)

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
            try:
                answer_btn.click()
                time.sleep(3)
                print("답변클릭")
            except:
                pass
        """
        # 태그 엘리먼트 기준으로 스크롤 처리 위한 전초작업
        answer_pos = self.driver.find_element_by_id('tagAreaForAnswer')

        # 태그 영역 보일때까지 스크롤 실제 이동
        if answer_pos.is_displayed:
            actions = ActionChains(self.driver)
            actions.move_to_element(answer_pos).perform()
            time.sleep(1)
        """

        # 답변하기 이전에 미리 업데이트 시켜놓아야 문제가 안생길듯 아래쪽은 브레이크 포인트가 있어서
        sql = "update kin set status = '1' where no = '" + str(kinno) + "'"
        self.curs.execute(sql)

        # 답변하기
        self.answer_run()

    # noinspection PyMethodMayBeStatic
    def answer_run(self):

        answer = self.get_rand_answer()
        pyperclip.copy(answer['content'])
        actions = ActionChains(self.driver)
        actions.key_down(Keys.CONTROL).send_keys('V').key_up(Keys.CONTROL).perform()

        answer_btn = self.driver.find_element_by_class_name('_answerRegisterButton')
        answer_btn.click()
        self.ui.logArea.append("답변버튼 클릭")

        time.sleep(2)

        while True:
            try:
                captcha = self.driver.find_element_by_id('au_captcha')
                time.sleep(1)
            except:
                break

            if captcha.is_displayed:
                self.ui.logArea.append("캡차출현")
                captchaurl = self.driver.find_element_by_css_selector('.popup__captcha_image img').get_attribute('src')
                response = requests.get(captchaurl)
                img = Image.open(BytesIO(response.content))
                img.save('captcha.jpg')
                api_key = os.getenv('APIKEY_2CAPTCHA', '51dfd4e96025f2921f2a695c6023e7f6')
                solver = TwoCaptcha(api_key)
                try:
                    result = solver.normal('captcha.jpg')
                except Exception as e:
                    # sys.exit(e)
                    break
                else:
                    self.ui.logArea.append("캡차해결번호 :" + result['code'])
                    captext = self.driver.find_element_by_id('input_captcha')
                    # 요기서 한번 클리어 처리
                    captext.click()
                    pyperclip.copy(result['code'])
                    captext.send_keys(Keys.CONTROL, 'a')
                    time.sleep(1)
                    captext.send_keys(Keys.CONTROL, 'v')
                    capbutton = self.driver.find_element_by_css_selector('._captcha_layer_close')
                    time.sleep(1)
                    capbutton.click()
                    time.sleep(1)
                    try:
                        Alert(self.driver).accept()
                    except:
                        pass
                    # sys.exit('solved: ' + str(result))
            else:
                break

    def get_rand_answer(self):

        sql = "select * from kin_answer where keyword = '" + self.mega_keyword + "' order by rand() limit 1"
        self.curs.execute(sql)
        result = self.curs.fetchall()
        kinset = {'no': result[0]['no'], 'content': result[0]['content']}
        return kinset

    def kin_list(self):
        # 로그인 인증처리
        if not self.login_check():
            return

        sql = "select * from kin where status = 0 and keyword = '" + self.mega_keyword + "' order by no desc"
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

        # keyword = self.ui.keyword.text()
        keyword = self.mega_keyword

        if self.mega_keyword:
            sql = "select * from kin_answer where member_id='" + self.mega_id + "' and keyword = '" + keyword + "' order by no desc"
        else:
            sql = "select * from kin_answer where member_id='" + self.mega_id + "' order by no desc"
        self.ui.logArea.append(sql)
        self.curs.execute(sql)
        rows = self.curs.fetchall()
        listtable = self.ui.answerListTable

        # 테이블 위젯에 행 적용
        listtable.setRowCount(len(rows))

        count = 0
        for row in rows:
            # 각 컬럼에 DB 값 연동처리
            listtable.setItem(count, 0, QTableWidgetItem(str(row['no'])))
            listtable.setItem(count, 1, QTableWidgetItem(row['keyword']))
            listtable.setItem(count, 2, QTableWidgetItem(row['content']))

            count += 1

    def answer_delete(self):
        insertno = self.ui.answerNo.text()
        if insertno:
            sql = "delete from kin_answer where no = %s"
            self.curs.execute(sql, (insertno))
            self.conn.commit()
            QMessageBox.about(self, "상태메시지", "삭제완료")
            self.ui.ansText.clear()
            self.ui.answerNo.clear()

            # 저장 후에 프레임 닫고 키워드리스트 다시불러오기 JJR 2021-01-05
            self.answer_frame_hide()
            self.init_keyword()

            self.answer_list()

    def answer_input(self):
        # title = self.ui.ansTitle
        content = self.ui.ansText.toPlainText()
        # keyword = self.ui.keyword.text()
        keyword = self.ui.keyword.text()

        self.selected_keyword = self.ui.keyword.text()
        insertno = self.ui.answerNo.text()

        if insertno:
            sql = "update kin_answer set content = %s where no = %s"
            self.curs.execute(sql, (content, int(insertno)))
        else:
            sql = "insert into kin_answer (member_id, keyword, content) values ( %s, %s, %s) "
            self.curs.execute(sql, (self.mega_id, keyword, content))
        try:
            self.ui.logArea.append(sql)
            self.conn.commit()

            # 저장 후에 프레임 닫고 키워드,글리스트 재호출해서 바뀐데이터 불러오기 JJR 2021-01-05
            self.answer_frame_hide()
            self.init_keyword()
            self.answer_list()

            return
        except Exception as e:
            print(e)

    def answer_clicked(self, row, column):
        print("Row %d and Column %d was clicked" % (row, column))

        self.ui.answerFrame.show()

        itemno = self.ui.answerListTable.item(row, 0)
        itemkeyword = self.ui.answerListTable.item(row, 1)
        itemcontent = self.ui.answerListTable.item(row, 2)

        self.ui.answerNo.setText(itemno.text())
        self.ui.keyword.setText(itemkeyword.text())
        self.ui.ansText.setText(itemcontent.text())

        print(itemno.text())

    def answer_input_form(self):

        self.ui.answerFrame.show()

        self.ui.answerNo.setText("")
        self.ui.keyword.setText("")
        self.ui.ansText.setText("")

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
        sql = "select count(*) as cnt from kin where status = 0 and keyword = '" + self.mega_keyword + "'"
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

    # 단순 테스트 버튼 활성화
    def naver_write_test(self):
        return

    # 답변수정 프레임 숨기기 JJR 2021-01-05
    def answer_frame_hide(self):
        self.ui.answerFrame.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    app.exec_()
