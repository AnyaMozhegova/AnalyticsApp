from mongoengine import FloatField


class NullableFloatField(FloatField):
    def validate(self, value):
        if value is not None:
            super().validate(value)

    def to_mongo(self, value):
        if value is None:
            return value
        return super().to_mongo(value)

    def to_python(self, value):
        if value is None:
            return value
        return super().to_python(value)
