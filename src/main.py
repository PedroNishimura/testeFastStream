import logging
import asyncio
from faststream import FastStream
from faststream.confluent import KafkaBroker
from typing import Any, Awaitable, Callable
from src.middlewares import InferenceMiddleware
from src.states import InferenceStatus

# Configuração do logger
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

global_inference_state = InferenceStatus.CONFIGURING
global_sends = 0

def main() -> FastStream:
    logger.info("🚀 Iniciando FastStream...")
    
    broker = KafkaBroker("kafka:9092")
    
    app = FastStream(broker=broker, logger=logger)

    @app.on_startup
    async def startup(c):
        await broker.start()

    async def subscriber_middleware(
    call_next: Callable[[Any], Awaitable[Any]],
    msg: str,
    ) -> Any:
        global global_inference_state
        global global_sends

        middleware = InferenceMiddleware(call_next, state=global_inference_state)
        global_inference_state = await middleware.on_receive()
        global_sends += 1
        
        try:
            result = await call_next(msg)
        except Exception as e:
            global_inference_state = await middleware.after_processed(type(e), e, e.__traceback__)
            raise e

        if (global_sends == 3):
            global_sends = 0
            global_inference_state = await middleware.after_processed(None, None, None)

        return result

    @broker.subscriber("meu_topico", middlewares=[subscriber_middleware])
    async def process_message(msg: dict):
        await asyncio.sleep(1)
        
        logger.info(f"📥 Mensagem recebida: {msg}")

    return app