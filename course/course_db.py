import pymysql
import json
class CoursesDB:
    def __init__(self):
        # 打开数据库连接
        self.db = pymysql.connect("localhost", "root", "Database6981228.", "course_ucas")
        self.db.set_charset("utf8")
        cursor = self.db.cursor()
        cursor.execute('SET NAMES utf8;')
        cursor.execute('SET CHARACTER SET utf8;')
        cursor.execute('SET character_set_connection=utf8;')

    def insert_course(self, course_name, course_id, course_code, season, course_time, location, weeks, school, school_id):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()

        # SQL 插入语句
        sql = "INSERT INTO course(course_name, \
                                        course_id, course_code, season, course_time, location, weeks, school, school_id) \
                                        VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
              (course_name, course_id, course_code, season, course_time, location, weeks, school, school_id)

        try:
            # 执行sql语句
            cursor.execute(sql)
            # 执行sql语句
            self.db.commit()
        except Exception as e:
            # 发生错误时回滚
            self.db.rollback()
            print("insert error! e:")
            print(e)

    def insert_student(self, student_name, student_number):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()

        # SQL 插入语句
        sql = "INSERT INTO student(`name`, `number`) \
                                               VALUES ('%s', '%s')" % \
              (student_name, student_number)

        try:
            # 执行sql语句
            cursor.execute(sql)
            # 执行sql语句
            self.db.commit()
        except Exception as e:
            # 发生错误时回滚
            self.db.rollback()
            print("insert error! e:")
            print(e)

    def insert_rela(self, student_num, course_id):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()

        # SQL 插入语句
        sql = "INSERT INTO rela_student_course(`student_num`, `course_id`) \
                                                       VALUES ('%s', '%s')" % \
              (student_num, course_id)

        try:
            # 执行sql语句
            cursor.execute(sql)
            # 执行sql语句
            self.db.commit()
        except Exception as e:
            # 发生错误时回滚
            self.db.rollback()
            print("insert error! e:")
            print(e)

    def get_all_course(self, school_id):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()

        # SQL 查询语句
        sql = "SELECT course_id, course_name FROM course WHERE school_id = '%s'" % school_id

        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            for row in results:
                # 打印结果
                print(row)
            return results
        except:
            print("Error: unable to fetch data")

    def get_courses_visited(self, student_name):
        # 使用cursor()方法获取操作游标
        cursor = self.db.cursor()

        # SQL 查询语句
        sql = "SELECT c.* FROM course as c, student as s, rela_student_course as r" \
              " WHERE r.student_num = s.number and r.course_id = c.course_id AND s.name = '%s'" % student_name

        try:
            # 执行SQL语句
            cursor.execute(sql)
            # 获取所有记录列表
            results = cursor.fetchall()
            for row in results:
                # 打印结果
                print(row)
            return results
        except:
            print("Error: unable to fetch data")

    def close(self):
        self.db.close()