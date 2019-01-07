from flask import Flask
from flask_bootstrap import Bootstrap
from flask import render_template
from flask import request
from flask import session
from flask import url_for
from flask import redirect
from flask import make_response
import os
import helper
import session
import uuid
import git

app = Flask(__name__)

# set bootstrap
Bootstrap(app)
uniq_id = os.urandom(24)
app.secret_key = uniq_id
app.env = helper.configx()["base"]["env"]


@app.route("/", methods=['GET'])
def base():
    if session.get(request.cookies.get('session')):
        return render_template('base.html')
    else:
        return redirect(url_for('login'))


@app.route("/login", methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['loginname']
        password = request.form['password']

        login_result = helper.sso(username, password)
        if login_result != "0":
            session.create({"data": {"username": username, "groups": login_result}, "key": request.cookies.get('session')})
            return redirect(url_for('base'))
        else:
            return render_template('login.html', msg="Failed to login")

    else:
        if session.get(request.cookies.get('session')):
            return redirect(url_for('base'))
        else:
            resp = make_response(render_template('login.html', msg="Please Login"))
            resp.set_cookie('session', str(uuid.uuid4()))
            return resp


@app.route("/logout", methods=['GET'])
def logout():
    session.delete(request.cookies.get('session'))
    return redirect(url_for('login'))


@app.route("/config/list", methods=['GET'])
def config_list():
    sess = session.get(request.cookies.get('session'))
    if sess:
        map_data = helper.check_user_group(sess)
        return render_template('config-list.html', map_data=map_data)
    else:
        return redirect(url_for('login'))


@app.route("/config/view/<env>/<squad>/<project>", methods=['GET'])
def config_view(env, squad, project):
    sess = session.get(request.cookies.get('session'))
    if sess:
        map_data = helper.check_user_group(sess)
        if project in map_data:
            if 'devops' in sess['groups']:
                editable = True
            else:
                editable = False

            config = helper.configx()
            data = config["mapping"][squad][project]

            service_cfg = helper.get_config_to_bb(env, project, data["dir"], data["file"])
            splitted = service_cfg.split('\n')
            service_cfg = "\n".join("<code>" + line + "</code>" for line in splitted)
            service_cfg = service_cfg.replace("<!", "{{")
            service_cfg = service_cfg.replace("!>", "}}")

            return render_template('config-view.html', service_cfg=service_cfg, service=project, squad=squad, env=env,
                                   editable=editable)
        else:
            return redirect(url_for('config_list'))
    else:
        return redirect(url_for('login'))


@app.route("/config/edit/<env>/<squad>/<project>", methods=['GET', 'POST'])
def config_edit(env, squad, project):
    sess = session.get(request.cookies.get('session'))
    if sess:
        map_data = helper.check_user_group(sess)
        if project in map_data:
            config = helper.configx()
            data = config["mapping"][squad][project]

            service_cfg = helper.get_config_to_bb(env, project, data["dir"], data["file"])
            line_count = len(service_cfg.split('\n'))
            return render_template('config-edit.html', service_cfg=service_cfg, service=project, squad=squad, env=env,
                                   line_count=line_count)
        else:
            return redirect(url_for('config_list'))
    else:
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
