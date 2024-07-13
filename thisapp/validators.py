from django.core.exceptions import ValidationError


def validate_file_size(file):
    max_size_mb = 50
    if file.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"The file size must not exceed {max_size_mb} MB.")
