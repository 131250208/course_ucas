# -*- coding:utf-8 -*-
import time, threading
import requests
from course import settings
from bs4 import BeautifulSoup
import re
from course.course_db import CoursesDB

class CourseCrawler:

    # 初始化时登录
    def __init__(self, username, pwd):

        login_url = "http://sep.ucas.ac.cn/slogin"
        payload_login = {
            "userName": username,
            "pwd": pwd,
            "sb": "sb",
        }
        self.session = requests.session()
        res = self.session.post(login_url, data=payload_login)
        print(res)
        self.school_map = {'数学学院': '910', '物理学院': '911', '天文学院': '957', '化学学院': '912', '材料学院': '928', '生命学院': '913', '地球学院': '914', '资环学院': '921', '计算机学院': '951', '电子学院': '952', '工程学院': '958', '经管学院': '917', '公共管理学院': '945', '人文学院': '927', '马克思中心': '964', '外语系': '915', '中丹学院': '954', '国际学院': '955', '存济医学院': '959', '体育教研室': '946', '微电子学院': '961', '未来技术学院': '962', '网络空间安全学院': '963', '心理学系': '968', '人工智能学院': '969', '纳米科学与技术学院': '970', '艺术中心': '971', '光电学院': '972', '创新创业学院': '967', }

    # 跳转进入选课系统
    def app_select(self):
        course_select_url = "http://sep.ucas.ac.cn/portal/site/226/821"
        res = self.session.get(course_select_url)

        soup = BeautifulSoup(res.text, "lxml")
        div = soup.select("div#main-content")
        jwxk = div[0].select("h4 > a")[0]['href']
        self.session.get(jwxk)

        res = self.session.get("http://jwxk.ucas.ac.cn/courseManage/main")
        soup = BeautifulSoup(res.text, "lxml")
        script = soup.select("script")[-1].text
        self.session_id = re.search('window.location = .*s=(.*)"', script).group(1)

    # 跳转进入课程网站
    def app_course(self):
        course_url = "http://sep.ucas.ac.cn/portal/site/16/801"
        res = self.session.get(course_url)
        soup = BeautifulSoup(res.text, "lxml")
        div = soup.select("div#main-content")

        course = div[0].select("a")[0]['href']  # 找到跳转链接
        res = self.session.get(course)
        soup = BeautifulSoup(res.text, "lxml")
        url = soup.select("frame#mainFrame")[0]['src']
        self.session_id = re.match(".*sakai.session=(.*?)&", url).group(1)
        res = self.session.get("http://course.ucas.ac.cn%s" % url)

    def get_course_time(self, course_id):
        res = self.session.get("http://jwxk.ucas.ac.cn/course/coursetime/%s" % (course_id))
        soup = BeautifulSoup(res.text, "lxml")
        tr_list = soup.select("table > tbody > tr")
        time = tr_list[0].select("td")[0].text
        location = tr_list[1].select("td")[0].text
        weeks = tr_list[2].select("td")[0].text

        return time, location, weeks

    def get_courses(self, school_id):
        course_list = []
        courses_url = "http://jwxk.ucas.ac.cn/courseManage/selectCourse"
        payload_selectCourse = {
            "deptIds": school_id,
            "sb": "sb",
        }
        res = self.session.post(courses_url, data=payload_selectCourse)
        soup = BeautifulSoup(res.text, "lxml")
        tr_list = soup.select("table > tbody > tr")
        for tr in tr_list:
            td_list = tr.select("td")
            span = td_list[2].select("span")[0]
            course_code = span.text
            coursetime_href = td_list[3].select("a")[0]["href"]
            course_id = coursetime_href.split("/")[-1]
            course_name = td_list[3].text
            time, location, weeks = self.get_course_time(course_id)
            print("%s %s %s %s %s %s" % (course_code, course_id, course_name, time, location, weeks))
            course_list.append({"course_code": course_code, "course_id": course_id, "course_name": course_name, "time": time, "location": location, "weeks": weeks})
        return course_list

    # 已选择的课程不会出现在院系的选课界面，所以要另外爬取
    def get_courses_selected(self):
        courses_url = "http://jwxk.ucas.ac.cn/courseManage/main"
        res = self.session.get(courses_url)
        soup = BeautifulSoup(res.text, "lxml")

        div = soup.select("div.mc-body")[-1]
        tr_list = div.select("table > tbody > tr")

        course_list = []
        for tr in tr_list:
            td_list = tr.select("td")
            course_code = td_list[0].select("a")[0].text

            coursetime_href = td_list[1].select("a")[0]["href"]
            course_id = coursetime_href.split("/")[-1]
            course_name = td_list[1].text
            time, location, weeks = self.get_course_time(course_id)
            print("%s %s %s %s %s %s" % (course_code, course_id, course_name, time, location, weeks))
            course_list.append({"course_code": course_code, "course_id": course_id, "course_name": course_name, "time": time, "location": location, "weeks": weeks})
        return course_list

    # 快速爬取课程信息，用于抢课，只返回从课程编码到课程id的映射map
    def get_course_fast(self, school_id):
        course_map = {}
        courses_url = "http://jwxk.ucas.ac.cn/courseManage/selectCourse"
        payload_selectCourse = {
            "deptIds": school_id,
            "sb": "sb",
        }
        res = self.session.post(courses_url, data=payload_selectCourse)
        soup = BeautifulSoup(res.text, "lxml")
        tr_list = soup.select("table > tbody > tr")
        for tr in tr_list:
            td_list = tr.select("td")
            span = td_list[2].select("span")[0]
            # a_href = td_list[2].select("a")[0]["href"]

            course_code = span.text.strip("★")
            # course_id = re.match("/course/courseplan/([0-9]+)", a_href).group(1)
            course_id = re.match("courseCode_([a-zA-Z0-9]+)", span['id']).group(1)
            # print("%s %s" % (course_code, course_id))
            course_map[course_code] = course_id
        return course_map


    def add_course(self, course_id):
        res = self.session.get("http://jwxk.ucas.ac.cn/courseManage/addCourseSite.json?courseId=%s" % (course_id))
        if "失败" in res.text:
            return False
        elif "成功" in res.text:
            return True
        else:
            print("%s %s" % (res.text, course_id))
            return False

    def del_course(self, course_id):
        url = "http://jwxk.ucas.ac.cn/courseManage/del/%s?s=%s" % (course_id, self.session_id)
        res = self.session.get(url)
        print(url)

    def get_students_info(self, course_id):
        students_list = []
        res = self.session.get("http://course.ucas.ac.cn/portal/site/%s" % course_id)
        soup = BeautifulSoup(res.text, "lxml")
        statisticsinfo_url = soup.select("a.icon-sakai-statisticsinfo")[0]['href']
        # print(statisticsinfo_url)
        res = self.session.get(statisticsinfo_url)
        soup = BeautifulSoup(res.text, "lxml")
        students_info_url = soup.select("iframe.portletMainIframe")[0]['src']
        res = self.session.get(students_info_url)

        soup = BeautifulSoup(res.text, "lxml")
        tr_list = soup.select("table.listHier > tr")
        for tr in tr_list[1:]: # 忽略标题行
            td_list = tr.select("td")
            # print("%s %s" % (td_list[1].text, td_list[2].text))
            students_list.append({"student_num": td_list[1].text, "student_name": td_list[2].text})

        return students_list

    def crawl_save_students_info(self, school_id):
        self.app_select()
        self.app_course()

        db = CoursesDB()
        course_ids = db.get_all_course(school_id)
        for row in reversed(course_ids):
            course_id = row[0]
            course_name = row[1]
            add_res = self.add_course(course_id)
            if add_res is True:
                print("正在进行课程 %s %s 的插入..." % (course_id, course_name))
                students_info = self.get_students_info(course_id)
                print(students_info)
                for st in students_info:
                    db.insert_student(st["student_name"], st["student_num"])
                    db.insert_rela(st["student_num"], course_id)
        db.close()

    def crawl_save_courses(self, school_id, school_name, season):
        self.app_select()

        course_list = self.get_courses(school_id)

        db = CoursesDB()
        for c in course_list:
            db.insert_course(c["course_name"], c["course_id"], c["course_code"], season, c["time"], c["location"], c["weeks"], school_name, school_id)
        db.close()

    def crawl_save_courses_selected(self, season):
        self.app_select()

        course_list = self.get_courses_selected()

        db = CoursesDB()
        for c in course_list:
            db.insert_course(c["course_name"], c["course_id"], c["course_code"], season, c["time"], c["location"],
                             c["weeks"], "已选遗漏课程", "-1")
        db.close()

    def crawl_school_id_name(self):
        self.app_select()

        school_map = {}
        res = self.session.get("http://jwxk.ucas.ac.cn/courseManage/main")
        soup = BeautifulSoup(res.text, "lxml")
        div_row_list = soup.select("div.row-fluid")
        for div in div_row_list:
            span2_list = div.select("div.span2")
            for span in span2_list:
                school_id = span.select("input")[0]['value']
                school_name = span.select("label")[0].text
                school_map[school_name] = school_id
        return school_map

    # 选课
    def select(self, school_id, course_id):

        payload = {
            "deptIds": school_id,
            "sids": course_id,
        }

        url = "http://jwxk.ucas.ac.cn/courseManage/saveCourse?s=%s" % self.session_id

        res = self.session.post(url, data=payload)
        soup = BeautifulSoup(res.text, "lxml")
        error_info = soup.select("div#messageBoxError > label")[0].text
        success_info = soup.select("div#messageBoxSuccess > label")[0].text

        print(error_info or success_info)
        if u"成功" in success_info or u"时间冲突" in error_info:# 时间冲突直接跳过，所以返回True
            return True
        elif u"超过限选人数" in error_info:
            return False
        else:
            return False

    # 爬全校所有学院的所有课程及参与课程的学生入库
    def crawl_save(self, season):
        # school_list = self.crawl_school_id_name()
        # for school_name, school_id in school_list.items():
        #     # if school_id not in ("951", "963", "964", "945"):
        #     self.crawl_save_courses(school_id, school_name, season)
        #     self.crawl_save_students_info(school_id)

        #补充已选的课程
        self.crawl_save_courses_selected(season)
        self.crawl_save_students_info("-1")

    def select_course_line(self, line, interval):
        match_ob = re.match("(.*):(.*)", line)
        school_id = ""
        try:
            school_id = self.school_map[match_ob.group(1)]
        except Exception as e:
            print(e)
            print("配置文件中存在不合法的学院名称")

        course_codes = match_ob.group(2).split(",")
        course_selected = []

        open_test = 0
        while True:
            course_map = self.get_course_fast(school_id)
            if len(course_map) != 0: break # 选课开放，跳出循环
            open_test += 1
            print("%d 课程网站上 %s 没有显示可选课程，选课可能还未开放...循环尝试中" % (open_test, match_ob.group(1)))
            time.sleep(interval)

        retry_test = 0
        while True:
            for ind, c_code in enumerate(course_codes):
                if ind not in course_selected:  # 只对未选中的进行尝试
                    course_id = ""
                    try:
                        course_id = course_map[c_code]
                    except Exception as e:
                        print(e)
                        print("%s 的 %s 找不到对应id" % (match_ob.group(1), c_code))
                        continue

                    if self.select(school_id, course_id):  # 选中则标记
                        course_selected.append(ind)
                        if len(course_selected) == len(course_codes):  # 判断结束
                            print("%s 选课完成！" % match_ob.group(1))
                            return

            retry_test += 1
            print("%d 对 %s 的未选中课程进行重新尝试..." % (retry_test, match_ob.group(1)))
            time.sleep(interval)
    # 按配置文件的配置信息进行抢课
    def select_courses_conf(self, interval = 0.0):
        # 解析配置文件,多线程循环抢课
        f = open("./conf", "r", encoding="utf8")
        thread_list = []
        for line in f:# 每行开一个线程进行抢课
            t = threading.Thread(target=self.select_course_line, args=(line, interval))
            t.start()
            thread_list.append(t)

        # 阻塞主线程等待所有线程结束
        for t in thread_list:
            t.join()

if __name__ == "__main__":

    courses_crawler = CourseCrawler(settings.USER_NAME, settings.PASSWORD)

    # # 爬取所有课程及选课学生信息
    # courses_crawler.crawl_save("春季")

    # 按配置文件conf抢课
    courses_crawler.app_select() # 先进入选课系统app
    courses_crawler.select_courses_conf(interval=0.5)

    # # 输出某学生课表
    # db = CoursesDB()
    # db.get_courses_visited(u"小张")

    pass


