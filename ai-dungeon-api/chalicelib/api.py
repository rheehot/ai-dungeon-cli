from typing import List, TypedDict

from chalicelib.ai_dungeon_cli.impl.api.client import AiDungeonApiClient
from chalicelib.ai_dungeon_cli.impl.utils.debug_print import debug_print


class ActionHistory(TypedDict):
    id: str
    text: str
    __typename: str


class AiSessionApiClient(AiDungeonApiClient):

    def __init__(self, access_token: str):
        super().__init__()
        self.update_session_access_token(access_token)
        self.scenario_id = 'scenario:458625'  # custom scenario id

    def create_session(self):
        debug_print("create session")
        result = self._execute_query('''
                mutation ($id: String, $prompt: String) {  createAdventureFromScenarioId(id: $id, prompt: $prompt) {    id    contentType    contentId    title    description    musicTheme    tags    nsfw    published    createdAt    updatedAt    deletedAt    publicId    historyList    __typename  }}
                ''',
                                     {
                                         "id": self.scenario_id,
                                         "prompt": None
                                     })
        debug_print(result)
        return result['createAdventureFromScenarioId']

    def _add_story(self, adventure_id: str, text: str):
        result = self._execute_query('''
               mutation ($input: ContentActionInput) {  sendAction(input: $input) {    id    actionLoading    memory    died    gameState    newQuests {      id      text      completed      active      __typename    }    actions {      id      text      __typename    }    __typename  }}
               ''',
                                     {
                                         "input": {
                                             "type": "story",
                                             "text": text,
                                             "id": adventure_id
                                         }
                                     })
        debug_print(result)
        return result['sendAction']

    def add_story(self, adventure_id: str, text: str) -> List[ActionHistory]:
        result = self._add_story(adventure_id, text)
        return result['actions'][-2:]

    def get_user_info(self):
        result = self._execute_query('''
        query { user {   id  gameSettings {  id  modelType  textSpeed    textSize    textFont     accessibilityMode   __typename    }  __typename  } }
        ''')
        print(result)
        return result
