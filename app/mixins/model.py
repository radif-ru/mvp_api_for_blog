class ModelDeleteMixin:
    def delete(self, using=None, keep_parents=False):
        """ Переопределение метода удаления для моделей.
        Вместо фактического удаления происходит
        архивирование - полю is_active присваивается False.
        """
        self.is_active: bool = False
        self.save()


class ModelPieceTextMixin:
    def piece_text(self):
        """ Сокращает текст, если он превышает допустимый объём.
        Модель должна содержать поле text.
        """
        text: str = self.text
        text_len: int = 100
        if len(text) < text_len:
            return text
        return f'{text[:text_len]}...'
