import json
import os

class FeedbackManager:
    def __init__(self, filepath="feedback_log.json"):
        self.filepath = filepath
        self.feedback_data = self._load_feedback()

    def _load_feedback(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {"likes": [], "dislikes": []}
        return {"likes": [], "dislikes": []}

    def save_feedback(self):
        with open(self.filepath, 'w') as f:
            json.dump(self.feedback_data, f, indent=2)

    def add_like(self, doc_id, topic_tags=None):
        if doc_id not in self.feedback_data["likes"]:
            self.feedback_data["likes"].append(doc_id)
            # Store tags/topics if available to refine future selection
            self.save_feedback()

    def add_dislike(self, doc_id):
        if doc_id not in self.feedback_data["dislikes"]:
            self.feedback_data["dislikes"].append(doc_id)
            self.save_feedback()

    def get_liked_ids(self):
        return set(self.feedback_data["likes"])
