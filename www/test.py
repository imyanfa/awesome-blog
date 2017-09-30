#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import orm
from models import User, Blog, Comment

def test_model():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(orm.create_pool(loop, user='admin', password='admin', db='awesome_blog'))
    
    user = User(email='admin@overflow.cc', passwd='123456', admin=True, name='Admin', image='about:blank')
    loop.run_until_complete(user.insert())
    user = User(email='test@overflow.cc', passwd='123456', name='Test', image='about:blank')
    loop.run_until_complete(user.insert())

    loop.run_until_complete(orm.destory_pool())
    loop.close()

if __name__ == '__main__':
    #test_model()
