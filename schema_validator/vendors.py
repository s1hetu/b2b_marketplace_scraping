"""
Schema validator for vendors
"""

vendor_validator = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["vendorId"],
        "properties": {
            "vendorId": {
                "bsonType": "string",
                "description": "must be a string and is required"
            },
            "source":{
                "bsonType": "string",
            },
            "company":{
                "bsonType": "string",
            },
            "companyDescription":{
                "bsonType": ["string", "null"],
            },
            "address":{
                "bsonType": ["string", "null"],
            },
            "locality":{
                "bsonType": ["string", "null"],
            },
            "city":{
                "bsonType": ["string", "null"],
            },
            "state":{
                "bsonType": ["string", "null"],
            },
            "country":{
                "bsonType": ["string", "null"],
            },
            "pincode": {
                "bsonType": ["string", "null"],
            },
            "email": {
                "bsonType": ["array"],
            },
            "categories": {
                "bsonType": ["array", "null"],
            },
            "phone":{
                "bsonType": ["array"],        
            },
            "website":{
                "bsonType": ["array"], 
            },
            "rating":{
                "bsonType": ["double", "string", "null"],
            },
            "totalReviews":{
                "bsonType": ["string", "null"],
            },
            "yearOfEstablishment":{
                "bsonType": ["string", "null"],
            },
            "turnover":{
                "bsonType": ["string","null"]
            },
            "gst":{
                "bsonType": ["string", "null"],       
            },
            "gstRegistrationDate":{
                "bsonType": ["string", "null"],
            },
            "owner":{
                "bsonType": ["string", "null"],
            },
            "numberOfEmployees":{
                "bsonType": ["string", "null"],
            },
            "gmaps":{
                "bsonType": ["string", "null"], 
            },
            "images":{
                "bsonType":["array"],
            },
            "timings":{
                "bsonType": ["string", "null"],
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