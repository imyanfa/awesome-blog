#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'jnuyanfa'

'''
A simple orm framework
'''

import logging; logging.basicConfig(level=logging.INFO, \
format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s')
import asyncio
import aiomysql
from datetime import datetime

async def create_pool(loop, **kw):
    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kw.get('host', 'localhost'),
        port=kw.get('port', 3306),
        user=kw['user'],
        password=kw['password'],
        db=kw['db'],
        charset=kw.get('charset', 'utf8'),
        autocommit=kw.get('autocommit', True),
        maxsize=kw.get('maxsize', 10),
        minsize=kw.get('minsize', 1),
        loop=loop 
    )

async def destory_pool():
    logging.info('destory database connection pool...')
    global __pool
    if __pool is not None:
        __pool.close()
        await __pool.wait_closed()

async def select(sql, args, size=None):
    logging.info('SQL: %s, params: %s' %(sql, args))
    global __pool
    async with __pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?', '%s'), args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('rows returned: %s' % len(rs))
        return rs

async def execute(sql, args, autocommit=True):
    logging.info('SQL: %s' %sql)
    global __pool
    async with __pool.acquire() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?', '%s'), args or ())
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        logging.info('affected %s rows' %affected)
        return affected

class Field(object):
    def __init__(self, name, column_type, primary_key, auto_update, default):
        self.name = name;
        self.column_type = column_type
        self.primary_key = primary_key
        self.auto_update = auto_update
        self.default = default
    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)

class StringField(Field):
    def __init__(self, name=None, primary_key=False, default=None, ddl='VARCHAR(127)'):
        super().__init__(name, ddl, primary_key, False, default)

class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, auto_update = False, default=0):
        super().__init__(name, 'INTEGER', primary_key, auto_update, default)

class LongFiled(Field):
    def __init__(self, name=None, primary_key=False, auto_update = False, default=0):
        super().__init__(name, 'BIGINT', primary_key, auto_update, default)

class FloatField(Field):
    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'REAL', primary_key, False, default)

class TextField(Field):
    def __init__(self, name=None, default=0.0):
        super().__init__(name, 'TEXT', False, False, default)

class TimestampField(Field):
    def __init__(self, name=None, primary_key=False, auto_update = False, default = datetime.now()):
        super().__init__(name, 'TIMESTAMP', primary_key, auto_update, default.strftime('%Y-%m-%d %H:%M:%S'))

def create_args_string(len):
    return ', '.join(['?' for x in range(len)])

class ModelMetaclass(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        table_name = attrs.get('__table__', None) or name
        logging.info('found model: %s(table: %s)' % (name, table_name))
        mapping = dict()
        fields = []
        insert_fields = []
        primary_key = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                logging.info('found maping: %s =====> %s' % (k, v))
                mapping[k] = v
                if v.primary_key:
                    if primary_key:
                        raise RuntimeError('Duplicate primary key: %s' %k)
                    primary_key = v.name or k
                fields.append(v.name or k)
                if not (v.auto_update):
                    insert_fields.append(v.name or k)
        #if not primary_key:
        #    raise RuntimeError('Primary key not found')

        for k in mapping.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        escaped_insert_fields = list(map(lambda f: '`%s`' % f, insert_fields))
        attrs['__mapping__'] = mapping
        attrs['__table__'] = table_name
        attrs['__primary_key__'] = primary_key
        attrs['__fields__'] = fields
        attrs['__insert_fields__'] = insert_fields
        attrs['__select__'] = 'SELECT %s FROM `%s`' % (','.join(escaped_fields), table_name)
        attrs['__insert__'] = 'INSERT INTO `%s` (%s) VALUES(%s)' % (table_name, ', '.join(escaped_insert_fields), \
                create_args_string(len(escaped_insert_fields)))
        attrs['__update__'] = 'UPDATE `%s`' % table_name
        attrs['__delete__'] = 'DELETE FROM `%s`' % table_name
        return type.__new__(cls, name, bases, attrs)

class Model(dict, metaclass=ModelMetaclass):
    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        if value is None:
            field = self.__mapping__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.debug('using default value for %s: %s' %(key, str(value)))
                setattr(self, key, value)
        return value
    
    @classmethod
    async def find_by_primary_key(cls, pk):
        if cls.__primary_key__ == None:
            raise RuntimeError('%s has no primary key' %cls.__class__.__name__)
        rs = await select('%s WHERE `%s` = ?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        else:
            return cls(**rs[0])
    
    @classmethod
    async def find(cls, where=None, args=None, **kw):
        sql = [cls.__select__]
        if where:
            sql.append('where') 
            sql.append(where)
        if args is None:
            args = []
        order_by = kw.get('order_by', None)
        if order_by:
            sql.append('order by')
            sql.append(order_by)
        limit = kw.get('limit', None)
        if limit:
            sql.append('limit')
            if isinstance(limit, int):
                sql.append('?')
                args.append(limit)
            elif (isinstance(limit, tuple) or isinstance(limit, list)) and len(limit) == 2:
                sql.append('?, ?')
                args.extend(limit)
            else:
                raise ValueError('Invalid limit value: %s' %limit)
        rs = await select(' '.join(sql), args)
        return [cls(**r) for r in rs]

    async def insert(self):
        args = list(map(self.getValueOrDefault, self.__insert_fields__))
        raws = await execute(self.__insert__, args)
        return raws

    async def update(self, where=None, args=None):
        final_args = [x for x in map(self.getValue, self.__fields__) if x is not None]
        conditions = [x for x in self.__fields__ if self.getValue(x) is not None]
        sql = [self.__update__]
        if conditions is None or len(conditions) == 0:
            return 0
        sql.append('SET')
        set_list = []
        for x in conditions:
            set_list.append('`%s` = ?' %x)
        sql.append(', '.join(set_list))
        if where:
            sql.append('WHERE')
            sql.append(where)
        if args is not None and len(args) > 0:
            final_args.extend(args)
        return await execute(' '.join(sql), final_args)

    async def delete(self):
        args = [x for x in map(self.getValue, self.__fields__) if x is not None]
        conditions = [x for x in self.__fields__ if self.getValue(x) is not None]
        sql = [self.__delete__]
        if args and len(args) > 0:
            sql.append('WHERE 1 = 1')
            for x in conditions:
                sql.append(' AND `%s` = ?' %x)
        return await execute(' '.join(sql), args)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(create_pool(loop, user='admin', password='admin', db='awesome_blog'))
    loop.run_until_complete(execute(r"insert into test (name) values (?)", ('caomao',)))
    result_list = loop.run_until_complete(select(r"select * from test", []))
    for result in result_list:
        print(result)
        # loop.run_until_complete(execute(r"delete from test where id = ?", (result.get('id', 0),)))
    loop.run_until_complete(destory_pool())
    loop.close()
