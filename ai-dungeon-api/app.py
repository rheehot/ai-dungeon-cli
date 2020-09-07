import os
from typing import List

from chalice import Chalice, Response

from chalicelib.api import AiSessionApiClient
from chalicelib.table import DEFAULT_PROMPT, History, Prompt, Session

AI_ACCESS_TOKEN = os.environ.get('AI_ACCESS_TOKEN')
app = Chalice(app_name='ai-dungeon-api')


class AiSession():
    def __init__(self, access_token: str):
        self.api = AiSessionApiClient(access_token)

    def create_session(self, name: str, prompt_name: str) -> Session:
        session = Session()
        session.name = name
        session.adventure_id = self.api.create_session()['id']
        prompt= Prompt.get(prompt_name)
        session.prompt = prompt_name
        actions = self.api.add_story(session.adventure_id, prompt.text)
        session.history = [
            History.from_prompt(**actions[0]),
            History.from_prompt_ai(**actions[1]),
        ]
        session.save()
        return session

    def send_msg(self, session: Session, text: str):
        actions = self.api.add_story(session.adventure_id, text)
        history = [
            History.from_user(**actions[0]),
            History.from_ai(**actions[1]),
        ]
        session.update([
            Session.history.set(Session.history.append(history)),
        ])
        session.refresh()
        return session


# 순서
# 커스텀 시나리오 기반 어드벤쳐 생성 -> 어드벤쳐 ID createAdventureFromScenarioId
# 스토리 추가 -> sendAction 뮤테이션 -> story 타입으로 추가 -> 첫번째 질의 응답 무시
# /

def get_session_or_404(session_id):
    try:
        session = Session.get(session_id)
    except Session.DoesNotExist:
        return Response(
            status_code=404,
            body=f'can not find {session_id} session'
        )
    return session


def check_required_fields(fields: List[str], data):
    for field in fields:
        if field not in data:
            return Response(
                status_code=400,
                body=f'{field} field required'
            )


@app.route('/sessions', methods=['POST'])
def create_session():
    session_api = AiSession(AI_ACCESS_TOKEN)
    data = app.current_request.json_body

    required_fields = ['prompt', 'name']
    resp = check_required_fields(required_fields, data)
    if resp:
        return resp
    session = session_api.create_session(data['name'], data['prompt'])
    return session.to_dict()


@app.route('/sessions', methods=['GET'])
def list_sessions():
    return {
        "results": [session.to_dict() for session in Session.scan()]
    }


@app.route('/sessions/{session_id}', methods=['GET'])
def get_session(session_id):
    session = get_session_or_404(session_id)
    if isinstance(session, Response):
        return session
    return session.to_dict()


@app.route('/sessions/{session_id}/message', methods=['POST'])
def send_msg(session_id):
    session = get_session_or_404(session_id)
    if isinstance(session, Response):
        return session
    data = app.current_request.json_body
    required_fields = ['message']
    resp = check_required_fields(required_fields, data)
    if resp:
        return resp

    session_api = AiSession(AI_ACCESS_TOKEN)
    session = session_api.send_msg(session, data['message'])
    result = session.to_dict()
    return result['history'][-1]


@app.route('/prompts', methods=['POST'])
def create_prompt():
    data = app.current_request.json_body
    required_fields = ['text', 'name']
    resp = check_required_fields(required_fields, data)
    if resp:
        return resp
    try:
        Prompt.get(data['name'])
        return Response(
            status_code=400,
            body=f'Duplicated prompt name : {data["name"]}'
        )
    except Prompt.DoesNotExist:
        prompt = Prompt()
        prompt.name = data['name']
        prompt.text = data['text']
        prompt.save()
        return prompt.to_dict()


@app.route('/prompts', methods=['GET'])
def list_prompts():
    return {
        "results": [s.to_dict() for s in Prompt.scan()]
    }


def get_prompt_or_404(name: str):
    try:
        prompt = Prompt.get(name)
    except Prompt.DoesNotExist:
        return Response(
            status_code=404,
            body=f'can not find {name} prompt'
        )
    return prompt


@app.route('/prompts/{name}', methods=['GET'])
def get_prompt(name):
    prompt = get_prompt_or_404(name)
    if isinstance(prompt, Response):
        return prompt
    return prompt.to_dict()


@app.route('/prompts/{name}', methods=["DELETE"])
def delete_prompt(name):
    if name in DEFAULT_PROMPT:
        return Response(status_code=400,
                        body='you can not delete default prompt')
    prompt = get_prompt_or_404(name)
    if isinstance(prompt, Response):
        return prompt
    prompt.delete()
    return Response(status_code=200,body=f'delete {name} prompt')

if __name__ == '__main__':
   session = AiSession(AI_ACCESS_TOKEN)
   session.api.get_user_info()
