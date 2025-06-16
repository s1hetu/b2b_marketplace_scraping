"""
Utils for generating score, apply scores into the database
"""
from database import db
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("ranking-main")


def generate_score(score_conditions, collection_name, add_existing_scores=False):
    """
    Generate scores based on the parameters and apply to the collection
    :param score_conditions: The condition to consider while generating/add score.
    :param collection_name: Name of the collection
    :param add_existing_scores: Flag to indicate whether to add the existing score or start with 0
    :return: List of dictionary to work as pipeline.
    """
    try:
        if add_existing_scores:
            conditions = {"$sum": [
                {"$ifNull": ["$score", 0]},  # Add existing `score` value (or 0 if missing)
                {"$sum": score_conditions}  # Add the newly calculated score
            ]
            }
        else:
            conditions = {"$sum": score_conditions}

        return [
            {"$addFields": {
                "score": conditions
            }
            },
            {
                "$merge": {
                    "into": collection_name,
                    "whenMatched": "merge",
                    "whenNotMatched": "discard",
                }
            }
        ]
    except Exception as error:
        logger.error(f"Error occurred while generating scores - {error}")


def apply_scores(pipeline, collection_name):
    """
    Main function to perform static scoring in specific collection with given pipeline
    :param pipeline: The pipeline to be aggregated.
    :param collection_name: Name of the collection.
    """
    try:
        collection = db.get_or_create_collection(collection_name)
        collection.aggregate(pipeline)
        logger.info(f"Scores calculated and updated successfully in the {collection_name} collection.")
    except Exception as error:
        logger.error(f"Error occurred while applying scores - {error}")
