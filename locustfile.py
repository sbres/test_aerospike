from locust import HttpLocust, TaskSet, task
import string
import random
import json

class MyTaskSet(TaskSet):
    @task
    def my_task(self):
        user = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))
        mail = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(25))
        password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(5))

        post = self.client.post('/singin', {'username': user, 'mail': mail, 'password': password}, catch_response=True)
        res = self.client.post('/login',  {'username': user, 'password': password}, catch_response=True)
        try:
            test = res.json()
            if test['mail'] == mail:
                res.success()
                post.success()
            else:
                res.failure('Not the same param !')
                post.failure('Not the same param !')
        except Exception, e:
            print e.message
            res.failure(e.message)
            post.failure(e.message)

class Simple_load(TaskSet):
    @task
    def get_page(self):
        self.client.get('/')


class MyLocust(HttpLocust):
    #host = "http://127.0.0.1:8000"
    #host = "http://dev-shosha-wa6yr4q2q5.elasticbeanstalk.com"
    host = "http://128.199.164.88:80"
    min_wait = 1000
    max_wait = 1000
    task_set = MyTaskSet
