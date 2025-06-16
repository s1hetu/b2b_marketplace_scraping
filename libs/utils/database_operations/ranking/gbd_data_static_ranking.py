"""Provide static ranking to the existing documents"""
from libs.utils.config import GOOGLE_BUSINESS_DATA_COLLECTION
from libs.utils.database_operations.ranking.scoring_pipeline import generate_score, apply_scores
from libs.utils.log_services.logger import setup_logger
from libs.utils.constants import GBD_FIELD_WEIGHTS

logger = setup_logger("gbd_static_ranking")

def main():
    """
     Aggregation pipeline
     Check if the field value is not null, [], "".
     Also check if value is positive (Yes, Active), add extra weights and assign scores accordingly.
    :return: list of added field and merge strategy
    """

    score_conditions = [
        {
            "$cond": [
                {
                    # Check if value is present
                    "$and": [
                        {"$ifNull": [f"${field}", False]},  # Field exists and is not null
                        {"$ne": [f"${field}", ""]},  # Field is not an empty string
                        {"$ne": [f"${field}", []]},  # Field is not an empty array
                    ]
                },
                {
                    # if value is present
                    "$cond": [
                        # check value is OPEN
                        {"$eq": [f"${field}", "OPEN"]},
                        # if the value is OPEN, increase weight by 1
                        weight + 1,
                        # else
                        {"$cond": [
                            # check value is True (bool)
                            {"$eq": [f"${field}", True]},
                            # if the value is True, increase weight by 1
                            weight + 1,
                            # else, assign weight
                            weight
                        ]
                        }
                    ]
                },
                # if value is not present, no scores for it
                0
            ]
        }
        for field, weight in GBD_FIELD_WEIGHTS.items()
    ]
    pipeline = generate_score(score_conditions, GOOGLE_BUSINESS_DATA_COLLECTION)
    apply_scores(pipeline, GOOGLE_BUSINESS_DATA_COLLECTION)


if __name__ == "__main__":
    main()
