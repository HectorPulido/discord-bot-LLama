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
        text = text.replace("?", "<qm>")

        translation = self.model_en_to_es(text)
        if len(translation) > 0:
            return translation[0]["translation_text"].replace("<qm>", "?")
        return text.replace("<qm>", "?")

    def spanish_to_english(self, text):
        text = text.replace("?", "<qm>")
        translation = self.model_es_to_en(text)
        if len(translation) > 0:
            return translation[0]["translation_text"].replace("<qm>", "?")
        return text.replace("<qm>", "?")
