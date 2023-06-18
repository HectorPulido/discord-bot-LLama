class MemoryModel:
    def __init__(self, memory_size=3, **kwargs):
        self.kwargs = kwargs
        self.memory_size = memory_size
        self.conversation = []
        self.last_response = ""

    def historial_conversation(self):
        conversarion_min = []
        if len(self.conversation) < self.memory_size:
            conversarion_min = self.conversation
        else:
            conversarion_min = self.conversation[-self.memory_size :]

        input_text = "\n".join([f"> {i}" for i in conversarion_min])
        return input_text

    def set_last_response(self, response):
        self.last_response = response

    def get_last_response(self):
        return self.last_response

    def clear_conversation(self):
        self.conversation.clear()

    def append_conversation(self, input_text):
        self.conversation.append(input_text)
