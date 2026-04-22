from pydantic import BaseModel

class ErrorResponse(BaseModel):
    status: str
    message: str
    error_code: str


# #Now use it in endpoints.

# @router.get(
#     "/tasks/{task_id}",
#     responses={
#         404: {
#             "model": ErrorResponse,
#             "description": "Task not found"
#         }
#     }
# )