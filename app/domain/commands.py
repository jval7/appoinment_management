import pydantic


class Command(pydantic.BaseModel):
    @classmethod
    def get_command_name(cls) -> str:
        return cls.__name__
