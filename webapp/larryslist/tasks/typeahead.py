from datetime import datetime
import logging, simplejson
from redis import StrictRedis
log = logging.getLogger(__name__)

def get_config_items(config, prefix):
    lenPref = len(prefix.split(".")) - 1
    return {'.'.join(k.split(".")[lenPref:]):config.get(k) for k in config.keys() if k.startswith(prefix)}
def get_typeahead_conn(params):
    return StrictRedis(host = params['host'], port = int(params['port']), db=params['db'])


class TypeAheadSearch(object):
    def __init__(self, project, conn, ttl = 60):
        self.project = project
        self.ttl = ttl

        self.conn = conn
        self.ns = u'{}:typeahead'.format(self.project)

        self.exists_key_f = lambda key: u'{}-{}:_exists'.format(self.ns, key)
        self.data_ns_f = lambda key: u'{}-{}:data'.format(self.ns, key)
        self.index_ns_f = lambda key: lambda idx: u'{}-{}:{}'.format(self.ns, key, idx)

    def invalidate(self, key):
        exists_key = self.exists_key_f(key)
        self.conn.delete(exists_key)

    def index(self, key, data):
        # Create the completion sorted set
        exists_key = self.exists_key_f(key)
        data_key = self.data_ns_f(key)
        index_key_f = self.index_ns_f(key)
        ttl = self.ttl

        last = self.conn.get(exists_key)
        if not last:
            p = self.conn.pipeline()

            l = sorted([(g.name.lower(), g.toQuery())  for g in data])
            for name, query in l:
                p.hset(data_key, query['value'], simplejson.dumps(query))
            p.execute()

            for name, query in l:
                elems = name.split()
                elems = set(elems + [' '.join(elems[i:]) for i, e in enumerate(elems)])
                for elem in elems:
                    for i,c in enumerate(elem):
                        pref = elem[0:i+1]
                        p.zadd(index_key_f(pref), len(elem)-len(pref), query['value'])
                        p.expire(index_key_f(pref), 3*ttl)
            p.execute()
            self.conn.setex(exists_key, ttl, datetime.now())
            log.info('UPDATED Elements in %s: %s', data_key, self.conn.hlen(data_key))


    def get(self, key, query, stringify = False, maxHits = 10):
        data_key = self.data_ns_f(key)
        index_key_f = self.index_ns_f(key)

        ids = self.conn.zrange(index_key_f(query.lower()), 0, -1)
        if ids:
            results = self.conn.hmget(data_key, ids[:maxHits])
        else:
            results = []
        return map(simplejson.loads, results)