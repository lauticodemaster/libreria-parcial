from sqlmodel import SQLModel


class EstadoVivo(SQLModel):
    estado: str


class EstadoListo(SQLModel):
    estado: str
    base: str
