#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'jnuyanfa'

from orm import Model, StringField, BooleanField, IntegerField, \
        LongField, FloatField, TextField, TimestampField

class User(Model):
    __table__ = 'user'

    id = IntegerField(primary_key=True, auto_update=True)
    email = StringField(ddl='VARCHAR(255)')
    passwd = StringField(ddl='VARCHAR(255)')
    admin = BooleanField()
    name = StringField(ddl='VARCHAR(255)')
    image = StringField(ddl='VARCHAR(255)')
    create_at = TimestampField(auto_update=True)
    update_at = TimestampField(auto_update=True)

class Blog(Model):
    __table__ = 'blog'

    id = IntegerField(primary_key=True, auto_update=True)
    user_id = IntegerField()
    user_name = StringField(ddl='VARCHAR(255)')
    user_image = StringField(ddl='VARCHAR(255)')
    name = StringField(ddl='VARCHAR(255)')
    summary = StringField(ddl='VARCHAR(255)')
    content = TextField()
    create_at = TimestampField(auto_update=True)
    update_at = TimestampField(auto_update=True)

class Comment(Model):
    __table__ = 'comment'

    id = IntegerField(primary_key=True, auto_update=True)
    user_id = IntegerField()
    blog_id = IntegerField()
    user_name = StringField(ddl='VARCHAR(255)')
    user_image = StringField(ddl='VARCHAR(255)')
    content = TextField()
    create_at = TimestampField(auto_update=True)
    update_at = TimestampField(auto_update=True)
