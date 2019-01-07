import yaml
import sys
import json
import requests
import ast


def log(msg):
    lg = json.dumps({"name": "chloe", "msg": msg}, ensure_ascii=False)
    sys.stderr.write(lg)
    return 0


def configx():
    with open("config/config.yaml", 'r') as stream:
        try:
            data = yaml.load(stream)
            return data
        except yaml.YAMLError as exc:
            log("Config file not found")


def sso(uid, pwd):
    config = configx()
    url = config["sso"]["url"]

    payload = {
        "username": uid,
        "password": pwd,
        "token": config["sso"]["token"],
        "attributes": ["uid", "memberof"]
    }
    headers = {
        "Content-Type": "application/json",
        "x-api-key": config["sso"]["x_api_key"]
    }
    r = requests.post(url, data=json.dumps(payload), headers=headers)

    if r.status_code != 200:
        log("Login Failed")
        return "0"
    else:
        user_data = ast.literal_eval(r.content)
        if "errorMessage" in user_data:
            log("Login Failed")
            return "0"
        else:
            user_member_of = user_data["memberof"]
            log("Login Success")
            return user_member_of


def check_user_group(sess):
    config = configx()
    data = {}

    if "devops" in sess['groups']:
        for map, val in config["mapping"].iteritems():
            for service, vl in val.iteritems():
                data[service] = map
    else:
        for map, val in config["mapping"].iteritems():
            if map in sess['groups']:
                for service, vl in val.iteritems():
                    data[service] = map
    return data


def get_config_to_bb(env, project, dr, fl):
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Basic %s" % (configx()["bitbucket"]["auth"])
    }

    url = "https://api.bitbucket.org/1.0/repositories/%s/config_management/raw/%s-%s/%s-%s/%s/%s" % (configx()["bitbucket"]["globaluser"], env, project, env, project, dr, fl)
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        log("failed connect to bitbucket: %s" % r.content)
        return "Config not available"
    else:
        return r.content

