"""Provide static ranking to the existing documents"""
from libs.utils.database_operations.ranking.scoring_pipeline import generate_score, apply_scores
from libs.utils.log_services.logger import setup_logger
from libs.utils.config import RAW_SCRAPED_DATA_COLLECTION
from libs.utils.constants import SCRAPED_DATA_FIELD_WEIGHTS

logger = setup_logger("static_ranking")


def main():
    """
     Aggregation pipeline
     Check if the field value is not null, [], "" and assign scores accordingly.
    :return: list of added field and merge strategy
    """
    score_conditions = [
        {"$cond":
            [
                {
                    "$and": [
                        {"$ifNull": [f"${field}", False]},
                        {"$ne": [f"${field}", ""]},
                        {"$ne": [f"${field}", []]},
                    ]
                },
                weight,
                0
            ]
        }
        for field, weight in SCRAPED_DATA_FIELD_WEIGHTS.items()
    ]
    pipeline = generate_score(score_conditions, RAW_SCRAPED_DATA_COLLECTION)
    apply_scores(pipeline, RAW_SCRAPED_DATA_COLLECTION)


if __name__ == "__main__":
    main()
