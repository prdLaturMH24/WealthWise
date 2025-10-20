import json
from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class ProviderSpecificFields:
    stop_reason: Optional[Any]
    token_ids: Optional[Any]


@dataclass
class Message:
    content: str
    role: str


@dataclass
class Choice:
    finish_reason: str
    index: int
    message: Message
    provider_specific_fields: ProviderSpecificFields


@dataclass
class Usage:
    completion_tokens: int
    prompt_tokens: int
    total_tokens: int


@dataclass
class ChatCompletion:
    id: str
    created: int
    model: str
    object: str
    choices: List[Choice] = field(default_factory=list)
    usage: Usage = None

    @staticmethod
    def from_json(json_str: str) -> "ChatCompletion":
        """
        Deserialize JSON string into a ChatCompletion object.
        """
        data = json.loads(json_str)

        choices = [
            Choice(
                finish_reason=c["finish_reason"],
                index=c["index"],
                message=Message(**c["message"]),
                provider_specific_fields=ProviderSpecificFields(**c["provider_specific_fields"])
            )
            for c in data["choices"]
        ]

        usage = Usage(**data["usage"])

        return ChatCompletion(
            id=data["id"],
            created=data["created"],
            model=data["model"],
            object=data["object"],
            choices=choices,
            usage=usage
        )
