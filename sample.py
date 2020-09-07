from pprint import pprint

import requests

host = 'https://prod.gpt-3.whatilearened.today'


# show prompt list

def get_prompts():
    prompts = requests.get(f"{host}/prompts").json()['results']
    for scen in prompts:
        print('='*10)
        print(scen['name'])
        print('-' * 10)
        print(scen['text'])
        print('=' * 10,'\n')

    return prompts


def create_session(name: str, prompt: str = 'qa'):
    data = {
        "name": name,
        "prompt": prompt,
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


def add_prompt(name, text):
    data = {
        "text": text,
        "name": name,
    }
    try:
        resp = requests.post(f"{host}/prompts", json=data).json()
        print(f'add {name} prompt')
    except Exception as e:
        print(e)


def delete_prompt(name):
    try:
        result = requests.delete(f"{host}/prompts/{name}")
        print(result.text)
    except Exception as e:
        print(e)


def main():
    get_prompts()
    name = 'test1'
    send_msg, show_history = create_session(name)

    q = 'Q: Who is Apple CEO?'
    print('\n\n', q)
    send_msg(q)

    q = 'Q: Who is MicroSoft CEO?'
    send_msg(q)

    print(f'\n\n{"#" * 6} print all history {"#" * 6}')
    pprint(show_history())


def custom_prompt():
    # add custom prompt
    new_prompt = 'word2text'
    new_prompt_text = """Word: piano
Text: I love piano!


Word: robot 
Text: I make robot. 


Word: happy 
Text: I'm so happy!


Word: macbook
Text: I will bye macbook.


Word: home
Text: I'm go home


"""
    add_prompt(new_prompt, new_prompt_text)
    name = 'test2'
    send_msg, show_history = create_session(name, prompt=new_prompt)
    show_history()

    q = 'Word: book\n'
    print(q)
    send_msg(q)

    print('\n\nfinish request')
    delete_prompt(new_prompt)


if __name__ == '__main__':
    main()
    custom_prompt()
