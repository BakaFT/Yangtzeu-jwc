import requests
from bs4 import BeautifulSoup
import re
import csv
import hashlib
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': 'http://jwc3.yangtzeu.edu.cn',
}
#cookies里的semesterid
# 16-17 44,45
# 17-18 46,48
# 18-19 49,69
# 19-20 89,109
# ....
login_session = requests.session()

def get_str_sha1_secret_str(res:str):
    sha = hashlib.sha1(res.encode('utf-8'))
    encrypts = sha.hexdigest()
    return encrypts
def login():
    username = '学号'
    password = '密码'
    captcha = ''
    login_url = 'http://jwc3.yangtzeu.edu.cn/eams/login.action'

    login_page_get = login_session.get(login_url,headers=headers)
    login_page_soup = BeautifulSoup(login_page_get.text, 'html.parser')

    def get_password_sha1(username, password):
        script = login_page_soup.find_all('script', {'type': 'text/javascript'})
        raw = script[4]
        text = raw.text
        pattern = r'CryptoJS.SHA1[(]\'(.*?)\''
        searchObj = re.search(pattern, text)
        if searchObj:
            login_key = re.search("'(.*)'", searchObj.group()).group().replace("'", '')
        else:
            print('获取Login Key失败')
        pwmix = get_str_sha1_secret_str(login_key + password)
        return pwmix
    password_sha1 = get_password_sha1(username,password)

    #登陆表单
    data = {
      'username': username,
      'password': password_sha1,
      'encodedPassword': '',
      'captcha_response': captcha,
      'session_locale': 'zh_CN'
    }

    login_page_post = login_session.post('http://jwc3.yangtzeu.edu.cn/eams/login.action',data=data ,verify=False)
login()
def getGrade():
    response_grade = login_session.get('http://jwc3.yangtzeu.edu.cn/eams/teach/grade/course/person!search.action?semesterId=89&projectType=',headers=headers)
    response_grade.encoding='utf-8'
    #print(response_grade.text)
    response_grade_soup = BeautifulSoup(response_grade.text, 'html.parser',)

    gridhead = response_grade_soup.find('thead', {'class': 'gridhead'}).find_all('th')
    firstLine = []
    for each in gridhead:
        firstLine.append(each.get_text())
    #print(firstLine)


    subjects_info = []
    Trees = response_grade_soup.find('tbody').find_all('tr')
    for tr in Trees:
        row = []
        for td in tr:
            astr = str(td.string)
            if astr.strip() != '': #滤掉空白字符串
                astr_fixed = ''.join(astr.split()) #去掉空格符 制表符和换行符
                row.append(astr_fixed)
            else:
                pass
        subject_info = dict(zip(firstLine,row))
        subjects_info.append(subject_info)
    return subjects_info
    #print(subjects_info)
subjects_info = getGrade()
def grade2csv():
    csvout1 = open('grade.csv', 'w', encoding='gbk', newline='')
    writer = csv.writer(csvout1)
    firstLine = ['学年学期', '课程代码', '课程序号', '课程名称', '课程类别', '学分', '总评成绩', '最终', '绩点']
    writer.writerow(firstLine)
    for dict_subject in subjects_info:
        row = []
        for value in dict_subject.values():
            row.append(value)
        writer.writerow(row)
grade2csv()

