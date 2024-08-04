from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

RESPONSES_KEY = 'responses'

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

@app.route('/')
def redirect_to_start():
    """ Start Survey"""
    if request.method == 'GET':
        return render_template('start_survey.html')

    # new_survey = SURVEY(name = request.form['name']) #SURVEY is the model
    # db.session.add(new_survey)db.session.commit()

@app.route('/start', methods=["POST"])
def start_survey():
    "Clear responses array"
    session[RESPONSES_KEY] = []

    return redirect('/questions/0')

@app.route('/questions/<int:questionid>')
def show_question(questionid):
    """Display current question"""

    # q: Question ordinal
    # question_num: Question index in the list
    # question: Question text
    responses = session.get(RESPONSES_KEY)

    if (responses is None):
        return redirect('/')

    #End questionnaire when all questions are answered
    if( len(responses) == len(survey.questions)):
        return redirect('/complete')
    
    #Enforce questions are answered in order
    if (len(responses) != questionid):
        flash("You can not move forward until you answer this question")
        return redirect(f"/questions/{len(responses)}")
    
    question = survey.questions[questionid]
    q = questionid + 1

    return render_template("question.html",
                           question_num = questionid,
                           question=question,
                           q = q)


@app.route('/answer', methods=["POST"])
def get_answer():
    """Save response and redirect to next question"""
    #get response choice
    choice = request.form['answer']

    # add response to the sesion
    responses = session[RESPONSES_KEY]
    responses.append(choice)
    session[RESPONSES_KEY] = responses
    return redirect(f"/questions/{len(responses)}")

@app.route('/complete')
def complete():
    return render_template('complete.html', responses=session[RESPONSES_KEY])