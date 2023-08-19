import os
import pickle
import logging
from memory import MemoryModel


class MultiChannelMemory:
    def __init__(self, memory_size=5, load_path=None):
        self.memories = {}
        self.memory_size = memory_size
        self.load_path = load_path

        if load_path is not None:
            self.load_memory()

    def persist_memory(self):
        if self.load_path is None:
            logging.info("No memory path specified...")
            return

        with open(self.load_path, "wb") as file:
            pickle.dump(self.memories, file)
            logging.info("Memory saved...")

    def load_memory(self):
        if self.load_path is None:
            logging.info("No memory path specified...")
            return False

        if not os.path.exists(self.load_path):
            logging.info("Memory file not found...")
            return False
        with open(self.load_path, "rb") as file:
            try:
                self.memories = pickle.load(file)
            except Exception as _:
                self.memories = {}
                logging.info("Memory not loaded...")
                return False
        logging.info("Memory Loaded...")
        return True

    def get_memory(self, channel_id):
        if channel_id not in self.memories:
            self.memories[channel_id] = MemoryModel(memory_size=self.memory_size)
        return self.memories[channel_id]

    def clear_channel_memory(self, channel_id):
        if channel_id in self.memories:
            del self.memories[channel_id]

    def clear_all_memory(self):
        self.memories = {}
        if self.load_path is not None:
            os.remove(self.load_path)
