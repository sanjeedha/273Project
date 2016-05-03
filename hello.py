from flask import Flask, request, jsonify

from fabric.api import run, execute
from fabric.context_managers import env
from fabric.contrib.files import exists

app = Flask(__name__)

# env.password = 'HR1234!!'

nodes = {'Node1': ['App1', 'App2'], 'Node2': ['App3']}


def create_folder_if_necessary(app_path):
    """
    Create the application folder if required
    :param app_path: folder path where application repo will be cloned.
    :return:
    """
    run('mkdir -p {}'.format(app_path))


def clone_or_update_git_repo(app_path, git_repo):
    """
    If the git code exists, update the repo. Else clone the repo.
    :param app_path: folder path where application repo will be cloned.
    :param git_repo: Git repo for the application
    :return:
    """
    # Check if git repo is already cloned in the folder. If yes, just update it.
    if exists('{}/.git'.format(app_path)):
        run('cd {} && git pull'.format(app_path))
    else:
        run('git clone {} {}'.format(git_repo, app_path))


def create_or_update_virtualenv(app_path):
    """
    Create virtualenv if it does not exist. Else update with latest pip requirements.
    :param app_path:
    :return:
    """
    virtualenv = '{}/../virtualenv'.format(app_path)
    if not exists('{}/bin/pip'.format(virtualenv)):
        run('virtualenv {}'.format(virtualenv,))
    run('{}/bin/pip install -r {}/requirements.txt'.format(virtualenv, app_path))


def start_application(app_path, app_name, port_num):
    """
    Start the application
    :param app_path:
    :return:
    """
    run('echo "export APP_PORT={}" >> {}/.env'.format(port_num, app_path))
    # run('mkdir -p /etc/service && cd / && ln -s /etc/service && cd /service')
    # run('mkdir -p /etc/sv && cp {}/service/{} /etc/sv/{} && ln -s /etc/sv/{}'.format(app_path, app_name, app_name, app_name))
    run('sv restart {}/service/{}'.format(app_path, app_name))


def host_type(app_name, git_repo, port_num):
    # run('cd ~/ && mkdir %s && cd %s && git clone %s' % (app_name, app_name, git_repo))
    app_path = '~/{}'.format(app_name)
    create_folder_if_necessary(app_path)
    clone_or_update_git_repo(app_path, git_repo)
    create_or_update_virtualenv(app_path)
    start_application(app_path, app_name, port_num)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/picloud", methods=['GET', 'POST'])
def picloud():
    if request.method == 'POST':
        content = request.json
        print content
        app_name = content['app-name']
        port_num = content['port']
        git_repo = content['git_repo']
        node_name = 'localhost'
        execute(host_type, app_name, git_repo, port_num, host=node_name)

        return jsonify(content)


if __name__ == "__main__":
    app.run()
