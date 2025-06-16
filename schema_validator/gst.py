"""
Schema validator for vendors
"""

gst_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["gst"],
        "properties": {
            "gst": {
                "bsonType": "string",
                "description": "must be a string, should be unique and is required"
            },
            "gstDetails":{
                "bsonType": "object",
            },
            "returnDetails":{
                "bsonType": "array",
            },
            "createdAt": {
                "bsonType": "date"
            },
            "updatedAt": {
                "bsonType": "date"
            }
        }
    }
}