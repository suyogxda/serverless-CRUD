import pydantic


class CreateUser(pydantic.BaseModel):
    email: str
    name: str
    password: str
    repassword: str

    @pydantic.validator("repassword")
    def passwords_match(cls, v, values, **kwargs):
        if "password" in values and v != values["password"]:
            raise ValueError("passwords do not match")
        return v


class SignIn(pydantic.BaseModel):
    email: str
    password: str
