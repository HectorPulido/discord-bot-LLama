from transformers import pipeline


class Translator:
    def __init__(self):
        self.model_en_to_es = pipeline(
            "translation", model="Helsinki-NLP/opus-mt-en-es"
        )
        self.model_es_to_en = pipeline(
            "translation", model="Helsinki-NLP/opus-mt-es-en"
        )

    def english_to_spanish(self, text):
        t = self.model_en_to_es(text)
        if len(t) > 0:
            return t[0]["translation_text"]
        return text

    def spanish_to_english(self, text):
        t = self.model_es_to_en(text)
        if len(t) > 0:
            return t[0]["translation_text"]
        return text
