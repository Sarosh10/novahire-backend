import random
import time
import speech_recognition as sr
import pyttsx3

from rapidfuzz import fuzz
from fpdf import FPDF

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AIInterviewAgent:

    def __init__(self):

        self.recognizer = sr.Recognizer()

        self.score = 0
        self.results = []

        self.candidate_name = ""
        self.interview_type = ""

        self.semantic_model = SentenceTransformer(
            'all-MiniLM-L6-v2'
        )

        self.questions = {

            "HR": {

                "Tell me about yourself": {

                    "keywords": [
                        "name", "myself", "engineering",
                        "student", "college", "background",
                        "education", "skills", "family",
                        "strength"
                    ],

                    "ideal":
                    "The answer should include introduction, education, background, and strengths."
                },

                "Why should we hire you": {

                    "keywords": [
                        "skills", "knowledge",
                        "hardworking", "teamwork",
                        "dedicated", "learn quickly",
                        "problem solving", "contribute",
                        "company growth", "responsible"
                    ],

                    "ideal":
                    "The answer should explain value, strengths, learning ability, and contribution to the company."
                },

                "What are your strengths": {

                    "keywords": [
                        "hardworking", "quick learner",
                        "teamwork", "communication",
                        "problem solving", "leadership",
                        "adaptable", "discipline"
                    ],

                    "ideal":
                    "The candidate should mention real strengths with confidence."
                }
            },

            "Technical": {

                "What is Ohm's law": {

                    "keywords": [
                        "voltage", "current",
                        "resistance", "v equals ir",
                        "relation", "proportional",
                        "ohm"
                    ],

                    "ideal":
                    "Ohm's law states that voltage is directly proportional to current at constant temperature. V = IR.",

                    "followup": [
                        "Can you tell me the formula of Ohm's law?",
                        "What happens to current if resistance increases?",
                        "Where is Ohm's law used in practical circuits?"
                    ]
                },

                "Difference between AC and DC": {

                    "keywords": [
                        "alternating", "direct",
                        "direction", "changes direction",
                        "constant direction",
                        "frequency", "ac", "dc"
                    ],

                    "ideal":
                    "AC changes direction periodically while DC flows in one direction."
                },

                "What is transformer": {

                    "keywords": [
                        "voltage", "step up",
                        "step down",
                        "electromagnetic induction",
                        "power transfer",
                        "magnetic field"
                    ],

                    "ideal":
                    "A transformer transfers electrical energy between circuits through electromagnetic induction."
                }
            }
        }

    # ---------------- SPEAK ---------------- #

    def speak(self, text):

        print("AI:", text)

        try:

            # SAME VOICE SYSTEM AS YOUR ORIGINAL CODE

            engine = pyttsx3.init("sapi5")

            engine.setProperty("rate", 165)
            engine.setProperty("volume", 1.0)

            voices = engine.getProperty("voices")

            if voices:
                engine.setProperty("voice", voices[0].id)

            engine.say(str(text))

            engine.runAndWait()

            engine.stop()

        except Exception as e:

            print("Speech error:", e)

            print("Text fallback:", text)

    # ---------------- LISTEN ---------------- #

    def listen(self, retries=2):

        for attempt in range(retries + 1):

            try:

                with sr.Microphone() as source:

                    print("Listening...")

                    self.recognizer.adjust_for_ambient_noise(
                        source,
                        duration=1
                    )

                    self.recognizer.energy_threshold = 300

                    self.recognizer.pause_threshold = 1

                    self.recognizer.dynamic_energy_threshold = True

                    start_time = time.time()

                    audio = self.recognizer.listen(
                        source,
                        timeout=6,
                        phrase_time_limit=12
                    )

                    response_time = (
                        time.time() - start_time
                    )

                    text = self.recognizer.recognize_google(
                        audio,
                        language="en-IN"
                    )

                    print("You:", text)

                    return (
                        text.lower(),
                        response_time,
                        "voice"
                    )

            except sr.WaitTimeoutError:

                print("No speech detected.")

                if attempt < retries:

                    self.speak(
                        "I did not hear anything. Please answer again."
                    )

            except sr.UnknownValueError:

                print("Could not understand audio.")

                if attempt < retries:

                    self.speak(
                        "I could not understand. Please speak clearly."
                    )

            except sr.RequestError:

                print("Speech service unavailable.")

                self.speak(
                    "Speech recognition unavailable. Please type your answer."
                )

                typed = input(
                    "Type your answer: "
                ).strip().lower()

                return typed, 8.0, "text"

            except Exception as e:

                print("Microphone error:", e)

                self.speak(
                    "Microphone problem. Please type your answer."
                )

                typed = input(
                    "Type your answer: "
                ).strip().lower()

                return typed, 8.0, "text"

        self.speak(
            "Switching to typed input."
        )

        typed = input(
            "Type your answer: "
        ).strip().lower()

        return typed, 10.0, "text"

    # ---------------- SEMANTIC AI ---------------- #

    def semantic_similarity(
            self,
            answer,
            ideal_answer
    ):

        try:

            embeddings = self.semantic_model.encode(
                [ideal_answer, answer]
            )

            score = cosine_similarity(
                [embeddings[0]],
                [embeddings[1]]
            )[0][0]

            return score

        except Exception as e:

            print("Semantic error:", e)

            return 0

    # ---------------- KEYWORD MATCH ---------------- #

    def check_similarity(
            self,
            answer,
            keywords
    ):

        if not answer.strip():
            return 0

        match = 0

        for word in keywords:

            similarity = fuzz.partial_ratio(
                word.lower(),
                answer.lower()
            )

            if similarity >= 70:
                match += 1

        return match

    # ---------------- EMOTION ---------------- #

    def detect_emotion(
            self,
            answer,
            response_mode,
            response_time
    ):

        positive_words = [
            "confident",
            "excited",
            "happy",
            "motivated"
        ]

        nervous_words = [
            "maybe",
            "not sure",
            "probably",
            "afraid"
        ]

        answer_lower = answer.lower()

        positive_score = sum(
            1 for word in positive_words
            if word in answer_lower
        )

        nervous_score = sum(
            1 for word in nervous_words
            if word in answer_lower
        )

        if nervous_score >= 2:
            return "Nervous"

        if positive_score >= 2:
            return "Confident"

        if response_mode == "voice" and response_time < 4:
            return "Confident"

        return "Neutral"

    # ---------------- CONFIDENCE ---------------- #

    def calculate_confidence_rating(
            self,
            answer,
            keyword_match,
            response_time,
            response_mode
    ):

        score = 0

        word_count = len(answer.split())

        if word_count >= 18:
            score += 30

        elif word_count >= 10:
            score += 20

        elif word_count >= 5:
            score += 10

        if keyword_match >= 4:
            score += 35

        elif keyword_match >= 2:
            score += 25

        elif keyword_match >= 1:
            score += 10

        if response_time <= 4:
            score += 20

        elif response_time <= 8:
            score += 10

        if response_mode == "voice":
            score += 15

        else:
            score += 5

        if score >= 80:
            return score, "High"

        if score >= 50:
            return score, "Medium"

        return score, "Low"

    # ---------------- ANSWER EVALUATION ---------------- #

    def evaluate_answer(
            self,
            answer,
            keywords,
            ideal_answer,
            response_time,
            response_mode
    ):

        if not answer.strip():

            return (
                0,
                "No answer detected.",
                0,
                "Low",
                "Neutral"
            )

        keyword_match = self.check_similarity(
            answer,
            keywords
        )

        semantic_score = self.semantic_similarity(
            answer,
            ideal_answer
        )

        confidence_score, confidence_label = (
            self.calculate_confidence_rating(
                answer,
                keyword_match,
                response_time,
                response_mode
            )
        )

        emotion = self.detect_emotion(
            answer,
            response_mode,
            response_time
        )

        total_score = keyword_match + (semantic_score * 5)

        if total_score >= 5:

            marks = 2
            feedback = "Good answer."

        elif total_score >= 2:

            marks = 1
            feedback = "Partially correct answer."

        else:

            marks = 0
            feedback = "Answer needs improvement."

        return (
            marks,
            feedback,
            confidence_score,
            confidence_label,
            emotion
        )

    # ---------------- INTERVIEW TYPE ---------------- #

    def choose_interview_type(self):

        print("\nSelect Interview Type")

        print("1. HR Interview")
        print("2. Technical Interview")
        print("3. Mixed Interview")

        while True:

            choice = input(
                "Enter choice (1/2/3): "
            ).strip()

            if choice == "1":
                return "HR"

            if choice == "2":
                return "Technical"

            if choice == "3":
                return "Mixed"

            print("Invalid choice.")

    # ---------------- BUILD QUESTIONS ---------------- #

    def build_question_list(self):

        if self.interview_type == "HR":

            questions = list(
                self.questions["HR"].items()
            )

            random.shuffle(questions)

            return questions

        if self.interview_type == "Technical":

            questions = list(
                self.questions["Technical"].items()
            )

            random.shuffle(questions)

            return questions

        hr_questions = list(
            self.questions["HR"].items()
        )

        tech_questions = list(
            self.questions["Technical"].items()
        )

        random.shuffle(hr_questions)

        random.shuffle(tech_questions)

        mixed = hr_questions + tech_questions

        random.shuffle(mixed)

        return mixed

    # ---------------- FINAL FEEDBACK ---------------- #

    def generate_final_feedback(
            self,
            percentage,
            avg_confidence
    ):

        if percentage >= 80 and avg_confidence >= 75:

            return (
                "Excellent performance with strong confidence."
            )

        if percentage >= 60:

            return (
                "Good performance. Improve clarity and depth."
            )

        if percentage >= 40:

            return (
                "Average performance. More practice required."
            )

        return (
            "Needs significant improvement."
        )

    # ---------------- TXT REPORT ---------------- #

    def save_report(
            self,
            final_percentage,
            avg_confidence,
            final_emotion,
            final_feedback
    ):

        with open(
                "result.txt",
                "w",
                encoding="utf-8"
        ) as file:

            file.write("AI INTERVIEW REPORT\n")

            file.write("=" * 60 + "\n")

            file.write(
                f"Candidate Name: {self.candidate_name}\n"
            )

            file.write(
                f"Interview Type: {self.interview_type}\n"
            )

            file.write(
                f"Final Score: {final_percentage:.2f}%\n"
            )

            file.write(
                f"Confidence Rating: {avg_confidence:.2f}\n"
            )

            file.write(
                f"Emotion: {final_emotion}\n"
            )

            file.write(
                f"Feedback: {final_feedback}\n\n"
            )

            for item in self.results:

                file.write(
                    f"Question: {item['question']}\n"
                )

                file.write(
                    f"Answer: {item['answer']}\n"
                )

                file.write(
                    f"Marks: {item['marks']}/2\n"
                )

                file.write(
                    f"Confidence: {item['confidence_score']}\n"
                )

                file.write(
                    f"Emotion: {item['emotion']}\n"
                )

                file.write(
                    "-" * 50 + "\n"
                )

    # ---------------- PDF REPORT ---------------- #

    def save_pdf_report(
            self,
            final_percentage,
            avg_confidence,
            final_emotion,
            final_feedback
    ):

        pdf = FPDF()

        pdf.add_page()

        pdf.set_font("Arial", "B", 16)

        pdf.cell(
            0,
            10,
            "AI INTERVIEW REPORT",
            ln=True
        )

        pdf.set_font("Arial", "", 12)

        pdf.cell(
            0,
            10,
            f"Candidate: {self.candidate_name}",
            ln=True
        )

        pdf.cell(
            0,
            10,
            f"Interview Type: {self.interview_type}",
            ln=True
        )

        pdf.cell(
            0,
            10,
            f"Final Score: {final_percentage:.2f}%",
            ln=True
        )

        pdf.cell(
            0,
            10,
            f"Confidence: {avg_confidence:.2f}",
            ln=True
        )

        pdf.cell(
            0,
            10,
            f"Emotion: {final_emotion}",
            ln=True
        )

        pdf.ln(5)

        pdf.multi_cell(
            0,
            8,
            f"Feedback: {final_feedback}"
        )

        pdf.output("interview_report.pdf")

    # ---------------- RUN ---------------- #

    def run(self):

        self.candidate_name = input(
            "Enter candidate name: "
        ).strip()

        if not self.candidate_name:
            self.candidate_name = "Candidate"

        self.interview_type = (
            self.choose_interview_type()
        )

        self.speak(
            f"Welcome {self.candidate_name}"
        )

        self.speak(
            f"You selected {self.interview_type} interview."
        )

        question_list = self.build_question_list()

        for i, (question, data) in enumerate(
                question_list,
                start=1
        ):

            print(f"\nQuestion {i}")

            self.speak(question)

            answer, response_time, input_mode = (
                self.listen()
            )

            (
                marks,
                feedback,
                confidence_score,
                confidence_label,
                emotion

            ) = self.evaluate_answer(

                answer,
                data["keywords"],
                data["ideal"],
                response_time,
                input_mode
            )

            self.score += marks

            # FOLLOW UP QUESTION

            if marks < 2 and "followup" in data:

                follow_question = random.choice(
                    data["followup"]
                )

                self.speak(follow_question)

                answer2, rt2, mode2 = self.listen()

                (
                    marks2,
                    feedback2,
                    conf2,
                    label2,
                    emo2

                ) = self.evaluate_answer(

                    answer2,
                    data["keywords"],
                    data["ideal"],
                    rt2,
                    mode2
                )

                self.score += marks2

                self.results.append({

                    "question":
                    follow_question,

                    "answer":
                    answer2,

                    "marks":
                    marks2,

                    "feedback":
                    feedback2,

                    "confidence_score":
                    conf2,

                    "emotion":
                    emo2
                })

            self.results.append({

                "question": question,

                "answer": answer,

                "marks": marks,

                "feedback": feedback,

                "confidence_score": confidence_score,

                "confidence_label": confidence_label,

                "emotion": emotion
            })

            self.speak(feedback)

        total_possible = len(self.results) * 2

        final_percentage = (
            self.score / total_possible
        ) * 100

        avg_confidence = sum(
            item["confidence_score"]
            for item in self.results
        ) / len(self.results)

        emotion_count = {}

        for item in self.results:

            emo = item["emotion"]

            emotion_count[emo] = (
                emotion_count.get(emo, 0) + 1
            )

        final_emotion = max(
            emotion_count,
            key=emotion_count.get
        )

        final_feedback = self.generate_final_feedback(
            final_percentage,
            avg_confidence
        )

        print("\nInterview Completed")

        print(
            f"Final Score: {final_percentage:.2f}%"
        )

        print(
            f"Confidence: {avg_confidence:.2f}"
        )

        print(
            f"Emotion: {final_emotion}"
        )

        print(
            f"Feedback: {final_feedback}"
        )

        self.speak(
            f"Your final score is {final_percentage:.2f} percent"
        )

        self.speak(
            final_feedback
        )

        # SAVE REPORTS

        self.save_report(
            final_percentage,
            avg_confidence,
            final_emotion,
            final_feedback
        )

        self.save_pdf_report(
            final_percentage,
            avg_confidence,
            final_emotion,
            final_feedback
        )

        self.speak(
            "Reports saved successfully"
        )


# ---------------- START PROGRAM ---------------- #

if __name__ == "__main__":

    agent = AIInterviewAgent()

    agent.run()