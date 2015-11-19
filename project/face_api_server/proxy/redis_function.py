import datetime
import json
import redis

redis_device_key = 'redis_device_key'
redis_send_key = 'redis_send_key'
device_expire_second = 300


class RedisProxy(object):
    def __init__(self, host='127.0.0.1', port=6379):
        self.redis_pool = redis.ConnectionPool(host=host, port=port, db=0)

    def connect(self):
        return redis.Redis(connection_pool=self.redis_pool)

    def get_device_datas(self):
        device_datas = []
        r = self.connect()
        result = r.hgetall(redis_device_key)

        remove_device_list = []

        for user_pair in result.items():
            values = user_pair[1].split('@')
            '''
            device_id = user_pair[0]

            update_time = datetime.datetime.strptime(values[1], "%Y-%m-%d %H:%M:%S.%f")

            now_time = datetime.datetime.today()
            expire_time_delta = datetime.timedelta(seconds=device_expire_second)

            if now_time > update_time + expire_time_delta:
                device_ids.append(device_id)
            else:
                remove_device_list.append(device_id)
            '''
            device_datas.append(json.loads(values[0]))

        self.remove_devices(remove_device_list)

        return device_datas

    def remove_devices(self, device_list):
        r = self.connect()
        p = r.pipeline()

        for device_id in device_list:
            p.hdel(redis_device_key, device_id)

        p.execute()

    def update_device(self, device_id, websocket_send_data):
        r = self.connect()
        insert_value = "%s@%s" % (json.dumps(websocket_send_data), datetime.datetime.now())
        return r.hset(redis_device_key, device_id, insert_value)

    def update_detection(self, device_id, identity):
        r = self.connect()

        result = r.hget(redis_send_key, identity)
        send_sms = False
        if result is not None:
            result_values = result.split('@')
            old_time = datetime.datetime.strptime(result_values[1], "%Y-%m-%d %H:%M:%S.%f")

            now_time = datetime.datetime.today()
            expire_time_delta = datetime.timedelta(seconds=device_expire_second)

            if now_time > old_time + expire_time_delta:
                send_sms = True

            if device_id != result_values[0]:
                send_sms = True

        else:
            send_sms = True

        if send_sms is True:
            insert_value = "%s@%s" % (str(device_id), datetime.datetime.now())
            result = r.hset(redis_send_key, identity, insert_value)

        return send_sms
