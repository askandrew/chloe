from rediscluster import StrictRedisCluster
import helper
import ast


startup_nodes = helper.configx()["redis"]["hosts"]
rc = StrictRedisCluster(startup_nodes=startup_nodes, decode_responses=True, skip_full_coverage_check=True)


def create(val):
    rc.set("chloe:" + val["key"], val["data"])
    return


def get(key):
    data = rc.get("chloe:%s" % key)
    if data is not None:
        return ast.literal_eval(data)
    else:
        return False


def delete(key):
    rc.delete("chloe:%s" % key)
    return True
