"""Provide static ranking to the existing documents"""
from libs.utils.config import GST_DATA_COLLECTION
from libs.utils.database_operations.ranking.scoring_pipeline import generate_score, apply_scores
from libs.utils.log_services.logger import setup_logger
from libs.utils.constants import GST_FIELD_WEIGHTS

logger = setup_logger("gst_static_ranking")


def main():
    """
     Aggregation pipeline
     Check if the field value is not null, [], "", NA, Not Applicable.
     Also check if value is positive (Yes, Active), add extra weights and assign scores accordingly.
    :return: list of added field and merge strategy
    """

    # todo: deduct points if status is suspended or inactive
    score_conditions = [
        {
            "$cond": [
                {
                    # Check if value is present
                    "$and": [
                        {"$ifNull": [f"${field}", False]},  # Field exists and is not null
                        {"$ne": [f"${field}", ""]},  # Field is not an empty string
                        {"$ne": [f"${field}", []]},  # Field is not an empty array
                        {"$ne": [f"${field}", "NA"]},  # Field is not "NA"
                        {"$ne": [f"${field}", "Not Applicable"]},  # Field is not "Not Applicable"
                    ]
                },
                {
                    # if value is present
                    "$cond": [
                        # check value is Yes
                        {"$eq": [f"${field}", "Yes"]},
                        # if the value is Yes, increase weight by 1
                        weight + 1,
                        # else
                        {"$cond": [
                            # check value is Active
                            {"$eq": [f"${field}", "Active"]},
                            # if the value is Active, increase weight by 3
                            weight + 3,
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
        for field, weight in GST_FIELD_WEIGHTS.items()
    ]
    pipeline = generate_score(score_conditions, GST_DATA_COLLECTION)
    apply_scores(pipeline, GST_DATA_COLLECTION)


if __name__ == "__main__":
    main()
