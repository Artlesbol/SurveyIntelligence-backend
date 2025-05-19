import datetime
import json

from django.http import JsonResponse
# Create your views here.
from django.views.decorators.csrf import csrf_exempt

from Qn.models import Survey, Submit, Answer
from epidemic.form import *


@csrf_exempt
def save_epidemic_answer_by_code(request):
    response = {'status_code': 1, 'message': 'success'}
    if request.method == 'POST':
        req = json.loads(request.body)
        code = req['code']  # 获取问卷信息
        answer_list = req['answers']
        username = request.session.get('username')
        if username is None:
            username = ''
        print("username" + username)
        survey = Survey.objects.get(share_url=code)
        if survey.is_deleted:
            response = {'status_code': 2, 'message': '问卷已删除'}
            return JsonResponse(response)

        if Submit.objects.filter(survey_id=survey, username=username,
                                 submit_time__gte=datetime.datetime.today().date()):
            response = {'status_code': 999, 'message': '当天已填写'}
            return JsonResponse(response)

        if not survey.is_released:
            return JsonResponse({'status_code': 4, 'message': '问卷未发布'})

        survey.recycling_num = survey.recycling_num + 1
        survey.save()

        submit = Submit(username=username, survey_id=survey, score=0)
        submit.save()
        for answer_dict in answer_list:
            question = Question.objects.get(question_id=answer_dict['question_id'])
            answer = Answer(answer=answer_dict['answer'], username=username,
                            type=answer_dict['type'], question_id=question, submit_id=submit)
            answer.save()

        return JsonResponse(response)

    else:
        response = {'status_code': -2, 'message': '请求错误'}
        return JsonResponse(response)


def judge_location(id):
    return JsonResponse({'status_code': 1, 'message': '低风险地区'})


def test(request):
    if request.method == 'POST':
        form = GetForm(request.POST)
        if form.is_valid():
            id = form.cleaned_data.get('question_id')
            return judge_location(id)
