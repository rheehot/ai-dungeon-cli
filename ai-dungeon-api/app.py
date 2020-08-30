import os
from typing import List

from chalice import Chalice, Response

from chalicelib.api import AiSessionApiClient
from chalicelib.table import DEFAULT_SCENE, History, Scene, Session

AI_ACCESS_TOKEN = os.environ.get('AI_ACCESS_TOKEN')
app = Chalice(app_name='ai-dungeon-api')


class AiSession():
    def __init__(self, access_token: str):
        self.api = AiSessionApiClient(access_token)

    def create_session(self, name: str, scene_name: str) -> Session:
        session = Session()
        session.name = name
        session.adventure_id = self.api.create_session()['id']
        scene = Scene.get(scene_name)
        session.scene = scene_name
        actions = self.api.add_story(session.adventure_id, scene.text)
        session.history = [
            History.from_scene(**actions[0]),
            History.from_scene_ai(**actions[1]),
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

    required_fields = ['scene', 'name']
    resp = check_required_fields(required_fields, data)
    if resp:
        return resp
    session = session_api.create_session(data['name'], data['scene'])
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


@app.route('/scenes', methods=['POST'])
def create_scene():
    data = app.current_request.json_body
    required_fields = ['text', 'name']
    resp = check_required_fields(required_fields, data)
    if resp:
        return resp
    try:
        Scene.get(data['name'])
        return Response(
            status_code=400,
            body=f'Duplicated scene name : {data["name"]}'
        )
    except Scene.DoesNotExist:
        scene = Scene()
        scene.name = data['name']
        scene.text = data['text']
        scene.save()
        return scene.to_dict()


@app.route('/scenes', methods=['GET'])
def list_scenes():
    return {
        "results": [s.to_dict() for s in Scene.scan()]
    }


def get_scene_or_404(name: str):
    try:
        scene = Scene.get(name)
    except Scene.DoesNotExist:
        return Response(
            status_code=404,
            body=f'can not find {name} scene'
        )
    return scene


@app.route('/scenes/{name}', methods=['GET'])
def get_scene(name):
    scene = get_scene_or_404(name)
    if isinstance(scene, Response):
        return scene
    return scene.to_dict()


@app.route('/scenes/{name}', methods=["DELETE"])
def delete_scene(name):
    if name in DEFAULT_SCENE:
        return Response(status_code=400,
                        body='you can not delete default scene')
    scene = get_scene_or_404(name)
    if isinstance(scene, Response):
        return scene
    scene.delete()
    return Response(status_code=200,body=f'delete {name} scene')
