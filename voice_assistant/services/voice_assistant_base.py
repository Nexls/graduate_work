from abc import ABC, abstractmethod
from typing import Union, Any, Awaitable


class VoiceAssistantServiceBase(ABC):

    @abstractmethod
    def get_top_films(self, *args, **kwargs) -> Union[Any, Awaitable[Any]]:
        ...
