from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class GetPromptComponentsRequest(_message.Message):
    __slots__ = ("spec_toml_content",)
    SPEC_TOML_CONTENT_FIELD_NUMBER: _ClassVar[int]
    spec_toml_content: str
    def __init__(self, spec_toml_content: _Optional[str] = ...) -> None: ...

class GetPromptComponentsResponse(_message.Message):
    __slots__ = ("components", "user_spec_prompt")
    class ComponentsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    USER_SPEC_PROMPT_FIELD_NUMBER: _ClassVar[int]
    components: _containers.ScalarMap[str, str]
    user_spec_prompt: str
    def __init__(self, components: _Optional[_Mapping[str, str]] = ..., user_spec_prompt: _Optional[str] = ...) -> None: ...
