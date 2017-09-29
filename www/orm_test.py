#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import orm
from orm import Model, IntegerField, StringField, TimestampField

class Test(Model):
    __table__ = 'test'

    id = IntegerField(primary_key = True, auto_update = True)
    name = StringField(ddl = 'VARCHAR(255)')
    createTime = TimestampField(name = 'create_time', auto_update = True)
    updateTime = TimestampField(name = 'update_time', auto_update = True)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop, user='admin', password='admin', db='awesome_blog'))
    test = loop.run_until_complete(Test.find_by_primary_key(18))
    print("select result is: ", test)
    #test = Test(name = 'testttt')
    #rows = loop.run_until_complete(test.insert())
    test_list = loop.run_until_complete(Test.find(where=r"name = ?", args=['test']))
    print(test_list)
    
    test = Test(name = 'hello')
    loop.run_until_complete(test.update(where=r'`name` = ?', args=['helo']))

    test = Test(name = 'hello')
    loop.run_until_complete(test.delete())

    loop.run_until_complete(orm.destory_pool())
    loop.close()
