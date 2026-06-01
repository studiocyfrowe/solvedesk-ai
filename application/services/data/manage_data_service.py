from api.requests.issue_request import IssueRequest

class ManageDataService:
    def __init__(self, embedder, vector_store):
        self.embedder = embedder
        self.vector_store = vector_store

    def get_single_issue(self, issue_id: int):
        self.vector_store.get_single_issue(issue_id=issue_id)

    def store_new_item(self, request: IssueRequest):
        document_text = (
            f"{request.issueName}\n"
            f"{request.issueSympthoms}\n"
            f"{request.issueSolution}"
        )

        emb = self.embedder.embed(document_text)
        
        self.vector_store.add_new(
            doc_id=str(request.issueItemId),
            embedding=emb,
            document=document_text,
            metadata={
                "issueItemId": request.issueItemId,
                "issueName": request.issueName,
                "issueSympthoms": request.issueSympthoms,
                "issueSolution": request.issueSolution
            }
        )

    def update_single_issue(self, issue_id: int, request: IssueRequest):
        document_text = (
            f"{request.issueName}\n"
            f"{request.issueSympthoms}\n"
            f"{request.issueSolution}"
        )

        emb = self.embedder.embed(document_text)
        
        self.vector_store.update_single_issue(
            doc_id=str(issue_id),
            embedding=emb,
            document=document_text,
            metadata={
                "issueItemId": request.issueItemId,
                "issueName": request.issueName,
                "issueSympthoms": request.issueSympthoms,
                "issueSolution": request.issueSolution
            }
        )

    def delete_single_issue(self, issue_id: int):
        self.vector_store.delete_single_issue(issue_id=issue_id)