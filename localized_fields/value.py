import collections

from django.conf import settings
from django.utils import translation


class LocalizedValue(dict):
    """Represents the value of a :see:LocalizedField."""

    def __init__(self, keys: dict=None):
        """Initializes a new instance of :see:LocalizedValue.

        Arguments:
            keys:
                The keys to initialize this value with. Every
                key contains the value of this field in a
                different language.
        """

        super().__init__({})
        self._interpret_value(keys)

    def get(self, language: str=None) -> str:
        """Gets the underlying value in the specified or
        primary language.

        Arguments:
            language:
                The language to get the value in.

        Returns:
            The value in the current language, or
            the primary language in case no language
            was specified.
        """

        language = language or settings.LANGUAGE_CODE
        return super().get(language, None)

    def set(self, language: str, value: str):
        """Sets the value in the specified language.

        Arguments:
            language:
                The language to set the value in.

            value:
                The value to set.
        """

        self[language] = value
        self.__dict__.update(self)
        return self

    def deconstruct(self) -> dict:
        """Deconstructs this value into a primitive type.

        Returns:
            A dictionary with all the localized values
            contained in this instance.
        """

        path = 'localized_fields.fields.LocalizedValue'
        return path, [self.__dict__], {}

    def _interpret_value(self, value):
        """Interprets a value passed in the constructor as
        a :see:LocalizedValue.

        If string:
            Assumes it's the default language.

        If dict:
            Each key is a language and the value a string
            in that language.

        If list:
            Recurse into to apply rules above.

        Arguments:
            value:
                The value to interpret.
        """

        for lang_code, _ in settings.LANGUAGES:
            self.set(lang_code, None)

        if isinstance(value, str):
            self.set(settings.LANGUAGE_CODE, value)

        elif isinstance(value, dict):
            for lang_code, _ in settings.LANGUAGES:
                lang_value = value.get(lang_code) or None
                self.set(lang_code, lang_value)

        elif isinstance(value, collections.Iterable):
            for val in value:
                self._interpret_value(val)

    def __str__(self) -> str:
        """Gets the value in the current language, or falls
        back to the primary language if there's no value
        in the current language."""

        value = self.get(translation.get_language())

        if not value:
            value = self.get(settings.LANGUAGE_CODE)

        return value or ''

    def __eq__(self, other):
        """Compares :paramref:self to :paramref:other for
        equality.

        Returns:
            True when :paramref:self is equal to :paramref:other.
            And False when they are not.
        """

        if not isinstance(other, type(self)):
            if isinstance(other, str):
                return self.__str__() == other
            return False

        for lang_code, _ in settings.LANGUAGES:
            if self.get(lang_code) != other.get(lang_code):
                return False

        return True

    def __ne__(self, other):
        """Compares :paramref:self to :paramerf:other for
        in-equality.

        Returns:
            True when :paramref:self is not equal to :paramref:other.
            And False when they are.
        """

        return not self.__eq__(other)

    def __setattr__(self, language: str, value: str):
        """Sets the value for a language with the specified name.

        Arguments:
            language:
                The language to set the value in.

            value:
                The value to set.
        """

        self.set(language, value)

    def __repr__(self):  # pragma: no cover
        """Gets a textual representation of this object."""

        return 'LocalizedValue<%s> 0x%s' % (dict(self), id(self))
