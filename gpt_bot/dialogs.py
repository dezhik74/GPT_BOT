
from typing import List, Dict, Optional

from gpt_bot import settings
from gpt_bot.tokens_num import num_tokens_from_message


class GPTMessage:
    role: str
    content: str
    tokens_num: int

    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content
        self.tokens_num = num_tokens_from_message(content)


class Dialog:
    telega_id: int
    messages: List[GPTMessage]

    def __init__(self, telega_id: int, messages: List):
        self.telega_id = telega_id
        self.messages = [m for m in messages]

    def __len__(self) -> int:
        return len(self.messages)

    def total_tokens_num(self) -> int:
        res = 0
        for m in self.messages:
            res = res + m.tokens_num
        return res

    def clear_messages(self, max_tokens: int = settings.MAX_TOKENS_IN_DIALOG):
        while self.total_tokens_num() >= max_tokens:
            del self.messages[0]

    def get_messages(self) -> List[Dict]:
        return [ {'role': m.role, 'content': m.content} for m in self.messages ]

    def append_message(self, role: str, message: str, max_tokens: int = settings.MAX_TOKENS_IN_DIALOG):
        self.messages.append(GPTMessage(role, message))
        self.clear_messages(max_tokens)

    def empty_messages(self):
        self.messages = []

class Dialogs:
    model: str
    dialogs: List[Dialog]

    def __init__(self, new_model: str = 'gpt-3.5-turbo-0301', new_dialogs: List[Dialog] = []):
        self.model = new_model
        self.dialogs = new_dialogs

    def __len__(self) -> int:
        return len(self.dialogs)

    def create_dialog(self, telega_id)  -> Optional[Dialog]:
        if self.get_dialog(telega_id) is None:
            d = Dialog(telega_id, [])
            self.dialogs.append(d)
            return d
        return None

    def get_dialog(self, telega_id: int) -> Optional[Dialog]:
        for d in self.dialogs:
            if d.telega_id == telega_id:
                return d
        return None

    def append_message_to_dialog(self, role: str, message: str, telega_id: int, max_tokens: int = settings.MAX_TOKENS_IN_DIALOG):
        d = self.get_dialog(telega_id)
        if d is None:
            d = self.create_dialog(telega_id)
        d.append_message(role, message, max_tokens)





