from flask import Flask, render_template, request, jsonify
from ai_voice_interview import AIInterviewAgent

app = Flask(__name__)

bot = AIInterviewAgent()

questions_data = []
current_question = 0


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start", methods=["POST"])
def start():

    global questions_data
    global current_question

    data = request.json

    interview_type = data["type"]

    bot.interview_type = interview_type

    questions_data = bot.build_question_list()

    current_question = 0

    first_question = questions_data[0][0]

    return jsonify({
        "question": first_question
    })


@app.route("/answer", methods=["POST"])
def answer():

    global current_question

    data = request.json

    user_answer = data["answer"]

    question, question_data = questions_data[current_question]

    marks, feedback, confidence_score, confidence_label, emotion = bot.evaluate_answer(

        user_answer,

        question_data["keywords"],

        question_data["ideal"],

        3,

        "voice"
    )

    current_question += 1

    if current_question < len(questions_data):

        next_question = questions_data[current_question][0]

    else:
        next_question = None

    return jsonify({

        "feedback": feedback,

        "confidence": confidence_score,

        "emotion": emotion,

        "next_question": next_question

    })


if __name__ == "__main__":
    app.run(debug=True)