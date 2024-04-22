"""
Memory model.
"""


class MemoryModel:
    """
    Class for memory models.
    """

    def __init__(self, memory_size=3, **kwargs):
        self.kwargs = kwargs
        self.memory_size = memory_size
        self.conversation = []
        self.last_response = ""

    def historial_conversation(self):
        """
        method for getting the conversation history
        """
        conversarion_min = []
        if len(self.conversation) < self.memory_size:
            conversarion_min = self.conversation
        else:
            conversarion_min = self.conversation[-self.memory_size :]

        return conversarion_min

    def set_last_response(self, response: str):
        """
        Last response setter
        """
        self.last_response = response

    def get_last_response(self) -> str:
        """
        Last response getter
        """
        return self.last_response

    def clear_conversation(self):
        """
        Method for clear conversation
        """
        self.conversation.clear()

    def append_conversation(self, input_text: str, role: str = "user"):
        """
        Method for append message to conversation
        """
        self.conversation.append(
            {
                "role": role,
                "content": input_text,
            }
        )

    def get_conversation_length(self) -> int:
        """
        Method for get conversation length
        """
        return len(self.conversation)
