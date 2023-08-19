from memory_model import MemoryModel

def test_memory():
    memory = MemoryModel(3)

    assert memory.get_conversation_length() == 0

    memory.append_conversation("Hola")
    memory.append_conversation("Como estas?")
    memory.append_conversation("Bien y tu?")

    assert memory.get_conversation_length() == 3

    memory.append_conversation("Muy bien")

    assert memory.get_conversation_length() == 3