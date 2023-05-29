class ModelDeleteMixin:
    def delete(self, using=None, keep_parents=False):
        """ Переопределение метода удаления для моделей.
        Вместо фактического удаления происходит
        архивирование - полю is_active присваивается False.
        """
        self.is_active: bool = False
        self.save()


class ModelPieceTextMixin:
    def piece_text(self, text_len: int or None = None) -> str:
        """ Сокращает текст, если он превышает допустимый объём.
        Модель должна содержать поле text.
        :param text_len - до какого количества необходимо сократить текст
        """
        text: str = self.text
        if not text_len:
            text_len: int = 100
        if len(text) < text_len:
            return text
        return f'{text[:text_len]}...'
