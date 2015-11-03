import redis

user_key = 'oldboy_user'
user_name_map_key = 'oldboy_name_map_key'

class RedisProxy(object):
    def __init__(self, host='127.0.0.1', port=6379):
        self.redis_pool = redis.ConnectionPool(host=host, port=port, db=0)

    def connect(self):
        return redis.Redis(connection_pool=self.redis_pool)

    def get_user(self, id):
        r = self.connect()
        item = r.hget(user_key, id)
        return item

    def get_user_by_name(self, name):
        r = self.connect()
        id = r.hget(user_name_map_key, name)

        if id is None:
            return None

        item = r.hget(user_key, id)
        return item

    def get_all_user(self):
        users = []
        r = self.connect();
        result = r.hgetall(user_key)

        for user_pair in result.items():
            values = user_pair[1].split(';')
            users.append((int(user_pair[0]), values[0], values[1]))

        return users

    def add_user(self, id, name, thumbnail):
        r = self.connect()
        r.hset(user_name_map_key, name, id)

        value = '%s;%s' % (name, thumbnail)
        return r.hset(user_key, id, value)

