from django import forms


def validate_positive_score(value):
    if value < 0.0:
        raise forms.ValidationError(
            'Баланс не может быть отрицательным',
            params={'value': value},
        )