"""
Test suite for the memory module
"""

import os
from memory_models import MemoryModel, MultiChannelMemory

PICKLE_PATH = "test.pkl"


def test_memory_size():
    """
    The memory size should be conscistent
    """
    memory = MemoryModel(3)

    assert memory.get_conversation_length() == 0

    memory.append_conversation("Hola")
    memory.append_conversation("Como estas?")
    memory.append_conversation("Bien y tu?")

    assert memory.get_conversation_length() == 3
    assert len(memory.historial_conversation()) == 3

    memory.append_conversation("Muy bien")

    # The conversation length is 4 but the memory size is 3 so
    # the historial_conversation should return the last 3 messages
    assert memory.get_conversation_length() == 4
    assert len(memory.historial_conversation()) == 3

    memory.clear_conversation()
    assert memory.get_conversation_length() == 0


def test_memory_last_response():
    """
    The last response should be conscistent
    """
    memory = MemoryModel(3)
    memory.set_last_response("Hola 1")
    assert memory.get_last_response() == "Hola 1"


def test_multichannel_memory_save():
    """
    The multichannel memory should be saved and loaded correctly
    """

    try:
        os.remove(PICKLE_PATH)
    except OSError:
        pass

    memory = MultiChannelMemory(3, PICKLE_PATH)
    assert len(memory.memories) == 0
    memory.get_memory(1).append_conversation("Hola 2")
    memory.get_memory(1).append_conversation("Como estas? 2")
    memory.persist_memory()

    assert os.path.exists(PICKLE_PATH)

    memory2 = MultiChannelMemory(3, PICKLE_PATH)
    assert len(memory2.memories) == 1
    assert memory2.get_memory(1).get_conversation_length() == 2

    os.remove(PICKLE_PATH)


def test_multichannel_clear():
    """
    The multichannel memory should be cleared correctly
    """

    memory = MultiChannelMemory(3)
    assert len(memory.memories) == 0
    memory.get_memory(1).append_conversation("Hola 3")
    memory.get_memory(1).append_conversation("Como estas? 3")
    memory.get_memory(2).append_conversation("Hola 4")
    memory.get_memory(2).append_conversation("Como estas? 4")

    assert memory.get_memory(1).get_conversation_length() == 2
    assert memory.get_memory(2).get_conversation_length() == 2

    memory.clear_channel_memory(1)
    assert memory.get_memory(1).get_conversation_length() == 0
    assert memory.get_memory(2).get_conversation_length() == 2

    memory.clear_all_memory()
    assert memory.get_memory(1).get_conversation_length() == 0
    assert memory.get_memory(2).get_conversation_length() == 0
