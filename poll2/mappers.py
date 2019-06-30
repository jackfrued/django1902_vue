from bpmappers import RawField
from bpmappers.djangomodel import ModelMapper

from poll2.models import Subject, Teacher


class SubjectMapper(ModelMapper):
    isHot = RawField('is_hot')

    class Meta:
        model = Subject
        exclude = ('create_date', 'is_hot')


class TeacherMapper(ModelMapper):
    goodCount = RawField('good_count')
    badCount = RawField('bad_count')

    class Meta:
        model = Teacher
        exclude = ('good_count', 'bad_count', 'subject')
