# course_ucas

## 功能
1. 抢课
2. 在抢课期间爬取课程信息，生成全校同学的课表。

## 配置
1. 在settings.py 中设置账号密码，如果只是选课，不必爬取课程信息，不需要设置数据库。
2. 在conf文件中配置抢课课单
```
学院名称:course_code1,course_code2,... # eg. 网络空间安全学院:201M7005H,201M7003H,201M7008H
```

## Quick Start 

**抢课**
```
# 登录
courses_crawler = CourseCrawler(settings.USER_NAME, settings.PASSWORD)
# 按配置文件conf抢课
courses_crawler.app_select() # 先进入选课系统app
courses_crawler.select_courses_conf(interval=0.5)# interval 为间隔时间
```

**爬取并导出课表**
```
# 登录
courses_crawler = CourseCrawler(settings.USER_NAME, settings.PASSWORD)

# 爬取所有课程及选课学生信息
courses_crawler.crawl_save("春季")

# 输出某学生课表
db = CoursesDB()
db.get_courses_visited(u"小张")
```
