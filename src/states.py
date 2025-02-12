from enum import Enum

class InferenceStatus(str, Enum):
    CONFIGURING = "sistema se configurando"
    WAITING = "aguardando proxima action"
    RUNNING = "inferencia rodando"
    ERROR = "ocorreu um erro"
    SUCCESS = "inferencia terminou com sucesso"