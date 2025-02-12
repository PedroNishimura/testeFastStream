import pytest
from src.middlewares import InferenceMiddleware
from src.states import InferenceStatus

@pytest.mark.asyncio
async def test_inference_middleware():
    """Testa a transição correta dos estados do middleware."""

    # Criamos um estado inicial para o teste
    state = {"status": InferenceStatus.CONFIGURING}
    middleware = InferenceMiddleware(state=state)

    # Passo 1: Primeira mensagem recebida -> Deve mudar para RUNNING
    await middleware.on_receive()
    assert state["status"] == InferenceStatus.RUNNING

    # Passo 2: Outra mensagem durante processamento -> Deve ser ignorada
    await middleware.on_receive()
    assert state["status"] == InferenceStatus.RUNNING  # Não deve mudar

    # Passo 3: Após o processamento sem erro -> Deve ir para SUCCESS
    await middleware.after_processed(None, None, None)
    assert state["status"] == InferenceStatus.SUCCESS

    # Passo 4: Nova mensagem após sucesso -> Deve mudar para WAITING e depois RUNNING
    await middleware.on_receive()
    assert state["status"] == InferenceStatus.RUNNING

    # Passo 5: Simular um erro no processamento
    await middleware.after_processed(Exception, Exception("Erro simulado"), None)
    assert state["status"] == InferenceStatus.ERROR

    # Passo 6: Nova mensagem após erro -> Deve voltar para WAITING e rodar novamente
    await middleware.on_receive()
    assert state["status"] == InferenceStatus.RUNNING