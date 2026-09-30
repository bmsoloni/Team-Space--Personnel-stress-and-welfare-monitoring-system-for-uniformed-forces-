from ..extensions import db
from datetime import datetime

class RagConversation(db.Model):
    __tablename__ = "rag_conversations"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    session_id = db.Column(db.String(64), nullable=False, index=True)
    use_case = db.Column(db.Enum("CHATBOT","RECOMMENDATION","CASE_SEARCH","EXPLANATION","COMPANION"), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    source_docs = db.Column(db.JSON, nullable=True)
    model_used = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id, "user_id": self.user_id,
            "session_id": self.session_id, "use_case": self.use_case,
            "question": self.question, "answer": self.answer,
            "source_docs": self.source_docs, "model_used": self.model_used,
            "created_at": self.created_at.isoformat(),
        }
