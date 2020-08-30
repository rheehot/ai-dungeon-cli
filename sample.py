from pprint import pprint

import requests

host = 'https://dev.gpt-3.whatilearened.today'


# show scene list

def get_scenes():
    scenes = requests.get(f"{host}/scenes").json()['results']
    for scen in scenes:
        print('='*10)
        print(scen['name'])
        print('-' * 10)
        print(scen['text'])
        print('=' * 10,'\n')

    return scenes


def create_session(name: str, scene: str = 'qa'):
    data = {
        "name": name,
        "scene": scene,
    }
    resp = requests.post(f"{host}/sessions", json=data).json()
    session_id = resp['id']

    def send_msg(msg):
        msg = requests.post(f"{host}/sessions/{session_id}/message", json={'message': msg}).json()
        print(msg['text'])
        return msg

    def show_history():
        results = requests.get(f"{host}/sessions/{session_id}").json()['history']
        for h in results:
            print('-' * 10)
            print(f"type: {h['history_by']}")
            print(f"{h['text']}")
            print('-' * 10)

    return send_msg, show_history


def add_scene(name, text):
    data = {
        "text": text,
        "name": name,
    }
    try:
        resp = requests.post(f"{host}/scenes", json=data).json()
        print(f'add {name} scene')
    except Exception as e:
        print(e)


def delete_scene(name):
    try:
        result = requests.delete(f"{host}/scenes/{name}")
        print(result.text)
    except Exception as e:
        print(e)


def main():
    get_scenes()
    name = 'test1'
    send_msg, show_history = create_session(name)

    q = 'Q: Who is Apple CEO?'
    print('\n\n', q)
    send_msg(q)

    q = 'Q: Who is MicroSoft CEO?'
    send_msg(q)

    print(f'\n\n{"#" * 6} print all history {"#" * 6}')
    pprint(show_history())


def custom_scene():
    # add custom scene
    new_scene = 'Make-Flask-Code'
    new_scene_text = """

Q: make return hello world app

CODE:
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'


Q: make request x,y and return x+y app 

CODE:
from flask import Flask
app = Flask(__name__)

@app.route('/{x}/{y}')
def sum_num():
    return x+y


Q: make get list of services app 

CODE:
from flask import Flask
app = Flask(__name__)

@app.route('/services')
def list_services():
    services = ['a','b']
    return services


Q: get list of people names app

CODE:
from flask import Flask
app = Flask(__name__)

@app.route('/peoples')
def list_names():
    names = ['sinsky','kendra']
    return names
    

"""
    add_scene(new_scene, new_scene_text)
    get_scenes()
    name = 'test2'
    send_msg, show_history = create_session(name, scene=new_scene)
    show_history()

    q = 'Q: make return bye app\n'
    print(q)
    send_msg(q)

    print('\n\nfinish request')
    delete_scene(new_scene)


if __name__ == '__main__':
    main()
    custom_scene()
