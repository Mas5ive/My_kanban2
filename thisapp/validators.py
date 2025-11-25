import os

from django.core.exceptions import ValidationError


def validate_file(file):
    allowed_extensions = ['.pdf', '.png', '.jpg', '.jpeg']
    max_size_mb = 5

    ext = os.path.splitext(file.name)[1]
    if ext.lower() not in allowed_extensions:
        raise ValidationError(f"File type not supported. Use one of {', '.join(allowed_extensions)}")

    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"The file size must not exceed {max_size_mb} MB.")
