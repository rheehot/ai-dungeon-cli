import json
import os
from datetime import datetime

import shortuuid
from pynamodb.attributes import ListAttribute, MapAttribute, UTCDateTimeAttribute, UnicodeAttribute
from pynamodb.models import Model

SessionDB = os.environ.get('SessionDB', 'ai-session-db-dev')
PromptDB = os.environ.get('PromptDB', 'ai-prompt-db-dev')


class BaseModel(Model):
    ignore_fields = []

    def to_json(self, indent=2):
        return json.dumps(self.to_dict(), indent=indent)

    def to_dict(self):
        ret_dict = {}
        for name, attr in self.attribute_values.items():
            if name not in self.ignore_fields:
                ret_dict[name] = self._attr2obj(attr)

        return ret_dict

    def _attr2obj(self, attr):
        # compare with list class. It is not ListAttribute.
        if isinstance(attr, list):
            _list = []
            for l in attr:
                _list.append(self._attr2obj(l))
            return _list
        elif isinstance(attr, MapAttribute):
            _dict = {}
            for k, v in attr.attribute_values.items():
                _dict[k] = self._attr2obj(v)
            return _dict
        elif isinstance(attr, datetime):
            return attr.isoformat()
        else:
            return attr


class Prompt(BaseModel):
    class Meta:
        table_name = PromptDB
        region = 'ap-northeast-2'

    name = UnicodeAttribute(hash_key=True)
    text = UnicodeAttribute()
    created_at = UTCDateTimeAttribute(default_for_new=datetime.utcnow)


class History(MapAttribute):
    id = UnicodeAttribute()
    text = UnicodeAttribute()
    history_by = UnicodeAttribute(default='user')

    @classmethod
    def from_user(cls, id: str, text: str, **kwargs):
        return cls(
            id=id,
            text=text,
            history_by='user'
        )

    @classmethod
    def from_ai(cls, id: str, text: str, **kwargs):
        return cls(
            id=id,
            text=text,
            history_by='ai'
        )

    @classmethod
    def from_prompt(cls, id: str, text: str, **kwargs):
        return cls(
            id=id,
            text=text,
            history_by='prompt'
        )

    @classmethod
    def from_prompt_ai(cls, id: str, text: str, **kwargs):
        return cls(
            id=id,
            text=text,
            history_by='scene_ai_return'
        )


class Session(BaseModel):
    class Meta:
        table_name = SessionDB
        region = 'ap-northeast-2'

    ignore_fields = ['adventure_id']

    id = UnicodeAttribute(hash_key=True, default_for_new=shortuuid.uuid)
    name = UnicodeAttribute()
    adventure_id = UnicodeAttribute()
    prompt = UnicodeAttribute()
    history = ListAttribute(of=History, default=list)
    created_at = UTCDateTimeAttribute(default_for_new=datetime.utcnow)


DEFAULT_PROMPT = {
    "qa": """
Q: What happens when you get the coronavirus disease?
A: People with COVID-19 generally develop signs and symptoms, including mild respiratory symptoms and fever, on an average of 5-6 days after infection (mean incubation period 5-6 days, range 1-14 days). Most people infected with COVID-19 virus have mild disease and recover.

Q: Which are the first symptoms of the coronavirus disease?
A: The virus can cause a range of symptoms, ranging from mild illness to pneumonia. Symptoms of the disease are fever, cough, sore throat and headaches. In severe cases difficulty in breathing and deaths can occur.

Q: Do strawberries need to be replanted every year?
A: In most climates, gardeners can plant strawberries as perennials. In this method, strawberry plants are planted about 1-1/2' apart, in rows about 4' apart. The plants will grow until they eventually form thick, lush rows about 2' wide. As they grow, they spread by sending out runners, which root right in the garden bed and produce daughter plants. By carefully managing a strawberry patch, a gardener growing strawberries as perennials can have berries for years to come, without ever having to buy another strawberry plant. Strawberry plants that are to be treated as annuals are planted closer together than those that are left to grow as perennials. For annuals, mound or hill up rows of soil about 6" or 8" tall, spacing the rows about 2' apart. Set the strawberries about 12" apart down the length of each mounded row. In areas with mild winters, plants are set out in the fall for a spring harvest; in colder climates with winter freezes, strawberries are set out in spring for a summer harvest. With the annual system, the strawberry plants are dug up and discarded after the harvest, and gardeners replant a crop of new, disease-free berries each year. It's an easy way to grow berries that works well for most people.

Q: What is the purpose of the self parameter of python methods?
A: The self parameter is a reference to the current instance of the class, and is used to access variables that belongs to the class.

Q: What part of the brain controls speech?
A: Damage to a discrete part of the brain in the left frontal lobe (Broca's area) of the language-dominant hemisphere has been shown to significantly affect the use of spontaneous speech and motor speech control.
""",
    "example-sentence":"""Word: book
Sentence: I like reading book!


Word: robot 
Sentence: I make robot.


Word: macbook
Sentence: I will bye macbook.


Word: home
Sentence: I'm go home
"""
}


def init_default_prompt():
    for name, text in DEFAULT_PROMPT.items():
        Prompt(
            name=name,
            text=text
        ).save()


if __name__ == '__main__':
    # init default prompt
    init_default_prompt()
    print([s.to_dict() for s in Prompt.scan()])