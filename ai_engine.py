from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


class AIEngine:

    def __init__(self):

        self.semantic_model = SentenceTransformer(
            'all-MiniLM-L6-v2'
        )

    def semantic_similarity(
            self,
            answer,
            ideal_answer
    ):

        embeddings = self.semantic_model.encode(
            [ideal_answer, answer]
        )

        score = cosine_similarity(
            [embeddings[0]],
            [embeddings[1]]
        )[0][0]

        return score

    def check_similarity(
            self,
            answer,
            keywords
    ):

        match = 0

        for word in keywords:

            similarity = fuzz.partial_ratio(
                word.lower(),
                answer.lower()
            )

            if similarity >= 70:
                match += 1

        return match

    def detect_emotion(self, answer):

        answer = answer.lower()

        positive_words = [
            "confident",
            "excited",
            "motivated"
        ]

        nervous_words = [
            "maybe",
            "not sure",
            "afraid"
        ]

        positive = sum(
            1 for word in positive_words
            if word in answer
        )

        nervous = sum(
            1 for word in nervous_words
            if word in answer
        )

        if nervous >= 2:
            return "Nervous"

        if positive >= 2:
            return "Confident"

        return "Neutral"

    def evaluate_answer(
            self,
            answer,
            keywords,
            ideal_answer
    ):

        keyword_match = self.check_similarity(
            answer,
            keywords
        )

        semantic_score = self.semantic_similarity(
            answer,
            ideal_answer
        )

        emotion = self.detect_emotion(
            answer
        )

        total_score = keyword_match + (
            semantic_score * 5
        )

        if total_score >= 5:

            feedback = "Good Answer"

        elif total_score >= 2:

            feedback = "Partially Correct"

        else:

            feedback = "Needs Improvement"

        return {

            "keyword_match": keyword_match,
            "semantic_score": float(semantic_score),
            "emotion": emotion,
            "feedback": feedback
        }