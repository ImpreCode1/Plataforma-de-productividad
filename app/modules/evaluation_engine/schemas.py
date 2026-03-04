from pydantic import BaseModel


class GenerationResponse(BaseModel):
    period_id: str
    total_users_processed: int
    total_evaluations_created: int
    total_results_created: int
    message: str