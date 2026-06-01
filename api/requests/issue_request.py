from pydantic import BaseModel

class IssueRequest(BaseModel):
    issueItemId: str
    issueName: str
    issueSympthoms: str
    issueSolution: str