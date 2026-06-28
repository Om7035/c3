import pytest
from core.context import ExecutionContext
from operators.placeholder import RetrieveOperator

@pytest.mark.asyncio
async def test_retrieve_operator():
    op = RetrieveOperator()
    context = ExecutionContext(query="test")
    res = await op.execute({}, context)
    assert res.success
    assert res.data["documents"] == ["doc1", "doc2"]
