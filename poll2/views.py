import json

import requests
from django.db.models import F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect

from poll2.captcha import Captcha
from poll2.forms import RegisterForm, LoginForm, TEL_PATTERN
from poll2.mappers import SubjectMapper, TeacherMapper
from poll2.models import Subject, Teacher, User
from poll2.utils import generate_captcha_code, generate_mobile_code


def index(request):
    return redirect('/static/subjects.html')


def get_mobile_code(request):
    """获得手机验证码"""
    tel = request.GET.get('tel')
    if TEL_PATTERN.fullmatch(tel):
        code = generate_mobile_code()
        request.session['mobile_code'] = code
        resp = requests.post(
            url='http://sms-api.luosimao.com/v1/send.json',
            auth=('api', 'key-6d2417156fefbd9c0e78fae069a34580'),
            data={
                'mobile': tel,
                'message': f'您的短信验证码是{code}，打死也不能告诉别人。【Python小课】',
            },
            timeout=3,
            verify=False
        )
        if json.loads(resp.text)['error'] == 0:
            code, hint = 20001, '短信验证码发送成功'
        else:
            code, hint = 20002, '短信验证码发送失败，请稍后重试'
    else:
        code, hint = 20003, '请输入有效的手机号码'
    return JsonResponse({'code': code, 'hint': hint})


def get_captcha(request):
    """生成图片验证码"""
    code = generate_captcha_code()
    request.session['captcha_code'] = code
    image_data = Captcha.instance().generate(code, fmt='PNG')
    return HttpResponse(image_data, content_type='image/png')


def logout(request):
    """用户注销"""
    request.session.flush()
    return redirect('index')


def login(request):
    """用户登录"""
    hint = ''
    backurl = request.GET.get('backurl', '/')
    if request.method == 'POST':
        backurl = request.POST['backurl']
        form = LoginForm(request.POST)
        if form.is_valid():
            code_from_session = request.session.get('captcha_code')
            code_from_user = form.cleaned_data['code']
            if code_from_session.lower() == code_from_user.lower():
                username = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = User.objects.filter(
                    username=username, password=password).first()
                if user:
                    request.session['userid'] = user.no
                    request.session['username'] = user.username
                    return redirect(backurl)
                else:
                    hint = '用户名或密码错误'
            else:
                hint = '请输入正确的验证码'
        else:
            hint = '请输入有效的登录信息'
    return render(request, 'login.html', {'hint': hint, 'backurl': backurl})


def register(request):
    """用户注册"""
    hint = ''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            code_from_session = request.session.get('mobile_code')
            code_from_user = form.cleaned_data['code']
            if code_from_session == code_from_user:
                form.save()
                hint = '注册成功，请登录!'
                return render(request, 'login.html', {'hint': hint})
            else:
                hint = '请输入正确的手机验证码'
        else:
            hint = '请输入有效的注册信息'
    return render(request, 'register.html', {'hint': hint})


def show_subjects(request):
    queryset = Subject.objects.all()
    subjects = []
    for subject in queryset:
        subjects.append(SubjectMapper(subject).as_dict())
    return JsonResponse(subjects, safe=False)


def show_teachers(request):
    """显示指定学科的老师"""
    sno = int(request.GET['sno'])
    queryset1 = Subject.objects.filter(no=sno)
    subject = SubjectMapper(queryset1.first()).as_dict()
    queryset2 = Teacher.objects.filter(subject__no=sno)
    teachers = []
    for teacher in queryset2:
        teachers.append(TeacherMapper(teacher).as_dict())
    return JsonResponse({'subject': subject, 'teachers': teachers})


def praise_or_criticize(request):
    """给老师点好评或者差评"""
    code, hint = 10002, '无效的老师编号'
    try:
        tno = int(request.GET['tno'])
        queryset = Teacher.objects.filter(no=tno)
        if queryset:
            if request.path.startswith('/praise/'):
                queryset.update(good_count=F('good_count') + 1)
            else:
                queryset.update(bad_count=F('bad_count') + 1)
            code, hint = 10001, '投票操作成功'
    except (KeyError, ValueError):
        pass
    return JsonResponse({'code': code, 'hint': hint})
