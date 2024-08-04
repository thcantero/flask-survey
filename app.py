from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

CURRENT_SURVEY_KEY = 'current_survey'
RESPONSES_KEY = 'responses'

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

@app.route('/')
def show_pick_survey_form():
    """Show pic a survey form"""
    return render_template('pick_survey.html', surveys=surveys)

@app.route('/', methods=['POST'])
def pick_survey():
    """Select a survey"""
    survey_id = request.form['survey_code']

    #don't allow to re-take survey
    survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id

    return render_template('start_survey.html', survey=survey)

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
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

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
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]
    return redirect(f"/questions/{len(responses)}")

@app.route('/complete')
def complete():
    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSES_KEY]

    return render_template('complete.html', survey=survey, responses=responses)