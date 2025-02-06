from google.protobuf.message import Message


def is_field_set(message: Message, field_name: str) -> bool:
    """
    Checks if a field is set in a Protobuf message, handling empty repeated fields.

    :param message: Protobuf message instance.
    :param field_name: Name of the field to check.
    :return: True if the field is set (even if empty), False otherwise.
    """
    if not isinstance(message, Message):
        raise TypeError("The provided object is not a Protobuf Message.")

    # Check if the field exists in the message
    field_descriptor = message.DESCRIPTOR.fields_by_name.get(field_name)
    if not field_descriptor:
        raise ValueError(f"Field '{field_name}' does not exist in the message.")

    # For repeated fields, check if the attribute exists (even if empty)
    value = getattr(message, field_name)
    if field_descriptor.label == field_descriptor.LABEL_REPEATED:
        return value is not None  # Always initialized, so it's set

    # For singular fields, check if it's explicitly set
    return field_name in {field.name for field, _ in message.ListFields()}
