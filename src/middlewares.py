import logging
from src.states import InferenceStatus
from faststream import BaseMiddleware

logger = logging.getLogger(__name__)

class InferenceMiddleware(BaseMiddleware):
    def __init__(self, call_next=None, state=None):
        """
        Construtor ajustado para aceitar apenas os parâmetros necessários.
        """
        super().__init__(call_next)
        self.inference_state = state

    async def on_receive(self):
        """Middleware para evitar concorrência na inferência."""
        logger.info(f"Entrou no Middleware e o status é esse {self.inference_state}")

        if self.inference_state == InferenceStatus.RUNNING:
            logger.warning("⚠️ Inferência já em andamento. Descartando mensagem.")

        if self.inference_state in {InferenceStatus.ERROR, InferenceStatus.SUCCESS}:
            self.inference_state = InferenceStatus.WAITING
            logger.info("⚠️ Inferência aguardando para ser iniciada.")

        if self.inference_state in {InferenceStatus.CONFIGURING, InferenceStatus.WAITING}:
            self.inference_state = InferenceStatus.RUNNING
            logger.info("🟢 Inferência iniciada.")

        return self.inference_state

    async def after_processed(self, exc_type, exc_val, exc_tb):
        """Garante que o estado é atualizado corretamente após o processamento."""
        if exc_type:
            self.inference_state = InferenceStatus.ERROR
            logger.error(f"❌ Erro na inferência: {exc_val}")
        else:
            self.inference_state = InferenceStatus.SUCCESS
            logger.info("✅ Inferência finalizada com sucesso.")

        return self.inference_state