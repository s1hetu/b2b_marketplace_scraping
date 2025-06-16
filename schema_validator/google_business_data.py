"""
Schema validator for google business data
"""

gbd_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["vendorId"],
        "properties": {
            "vendorId": {
                "bsonType": "string",
                "description": "must be a string, should be unique and is required"
            },
            "data":{
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