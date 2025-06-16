"""
File containing common utility functions to be used across different databaase operations modules
"""
import re

def snake_to_camel(snake_str):
    """
    Convert snake_case or space-separated strings to camelCase.

    Args:
        snake_str: The string to be converted from snake case to camelCase.

    Returns:
        The converted string.
    """
    components = re.split(r' |_|-', snake_str)
    return components[0].lower() + ''.join(x.title() for x in components[1:])

def convert_keys_to_camel_case(data, convert_nested_keys=False):
    """Convert all dictionary keys to camelCase recursively.

    Args:
        data: The data from which keys need to be converted.
        convert_nested_keys: A flag to control if nested keys should be converted.

    Returns:
        The data with converted keys.
    """
    if isinstance(data, list):
        return [convert_keys_to_camel_case(item, convert_nested_keys) for item in data]
    elif isinstance(data, dict):
        # Convert the current level keys
        converted_data = {snake_to_camel(key): value for key, value in data.items()}
        if convert_nested_keys:
            # Recursively convert nested dictionary keys
            for key, value in converted_data.items():
                if isinstance(value, (dict, list)):
                    converted_data[key] = convert_keys_to_camel_case(value, convert_nested_keys)
        return converted_data
    else:
        return data
