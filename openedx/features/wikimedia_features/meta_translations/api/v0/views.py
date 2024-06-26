"""
Views for MetaTranslation v0 API(s)
"""
import copy

from rest_framework import generics, status, permissions, pagination
from rest_framework.response import Response
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import UsageKey, CourseKey
from django.utils.translation import ugettext as _

from cms.djangoapps.contentstore.views.course import get_courses_accessible_to_user
from common.lib.xmodule.xmodule.modulestore.django import modulestore
from lms.djangoapps.courseware.courses import get_course_by_id
from openedx.features.wikimedia_features.meta_translations.api.v0.utils import (
    get_courses_of_base_course, get_outline_course_to_units, get_outline_unit_to_components
    )
from openedx.features.wikimedia_features.meta_translations.models import CourseBlock, CourseTranslation, TranslationVersion
from openedx.features.wikimedia_features.meta_translations.api.v0.serializers import (
    CourseBlockTranslationSerializer, CourseBlockVersionSerializer, MetaCourseTranslationSerializer,
    TranslationVersionSerializer, MetaCoursesSerializer,
)
from common.djangoapps.student.roles import CourseStaffRole

class GetTranslationOutlineStructure(generics.RetrieveAPIView):
    """
    API to get course outline of a course and it's base course
    Response:
        {
            "course_info": {
                "usage_key":"course key",
                "category":"course",
                "data_block_ids: {
                    "display_name": 1,
                },
                "data":{
                    "display_name":"Course Name",
                }
                "status": {
                    "applied": false,
                    "approved": false,
                    "last_fetched": null,
                    "approved_by": edx
                },
            },
            "course_outline": {
                "7VLKTTPX1ZUJI8KA":{
                    "usage_key":"block_component_usage_id",
                    "category":"vertical",
                    "data_block_ids: {
                        "display_name": 1,
                    },
                    "data":{
                        "display_name":"Problem 1",
                    }
                    "status": {
                        "applied": false,
                        "approved": false,
                        "last_fetched": null,
                        "approved_by": edx
                    },
                    children: {
                        "8KLKTTPX1ZUJI8KA": {
                            "usage_key":"block_component_usage_id",
                            "category":"vertical",
                            "data_block_ids: {
                                "display_name": 2,
                            },
                            "status": {
                                "applied": false,
                                "approved": false,
                                "last_fetched": null,
                                "approved_by": edx
                            },
                            "data": {
                                "display_name": "Section 1"
                            }
                            children: {
                                "9LLKTTPX1ZUJI8KA" {
                                    "usage_key":"block_component_usage_id",
                                    "category":"horizontal",
                                    "data_block_ids: {
                                        "display_name": 2,
                                    },
                                    "data: {
                                        "display_name": "Unit 1",
                                    },
                                }
                            }
                        }
                    }
                }
            },
            "base_course_inf": {
                "usage_key":"base_course key",
                "category":"course",
                "data":{
                    "display_name":"Base Course Name",
                }
            }
            "base_course_outline": {
                "7VLKTTPX1ZUJI8KA":{
                    "usage_key":"base_block_component_usage_id",
                    "category":"vertical",
                    "data":{
                        "display_name":"Problem 1",
                    }
                    children: {
                        "8KLKTTPX1ZUJI8KA": {
                            "usage_key":"base_block_component_usage_id",
                            "category":"vertical",
                            "data": {
                                "display_name": "Section 1"
                            }
                            children: {
                                "9LLKTTPX1ZUJI8KA" {
                                    "usage_key":"base_block_component_usage_id",
                                    "category":"horizontal",
                                    "data: {
                                        "display_name": "Unit 1",
                                    },
                                }
                            }
                        }
                    }
                }
            }
        }
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        course_id = kwargs.get('course_key')
        course_key = CourseKey.from_string(course_id)
        course = get_course_by_id(course_key)

        course_outline, base_course_outline = get_outline_course_to_units(course)

        if course_outline and base_course_outline:
            key, base_key = list(course_outline.keys())[0], list(base_course_outline.keys())[0]
            course_info, base_course_info = copy.deepcopy(course_outline[key]), copy.deepcopy(base_course_outline[key])
            course_info['children'], base_course_info['children'] = [], []
            course_outline, base_course_outline = course_outline[key]['children'], base_course_outline[base_key]['children']

        data = {
            'course_info': course_info,
            'base_course_info': base_course_info,
            'course_outline': course_outline,
            'base_course_outline': base_course_outline,
        }

        return Response(data, status=status.HTTP_200_OK)

class GetVerticalComponentContent(generics.RetrieveAPIView):
    """
    API to get component data of a course and it's base course
      Response:
        {
            'course_outline': {
                "7VLKTTPX1ZUJI8KA":{
                    "usage_key":"block_component_usage_id",
                    "category":"problem",
                    "data_block_ids: {
                        "display_name": 1,
                        "content": 10
                    },
                    "status": {
                        "applied": false,
                        "approved": false,
                        "last_fetched": null,
                        "approved_by": edx
                    },
                    "data":{
                        "display_name":"Problem 1",
                        "content":""
                    }
                },
                "B36BXKA90A56Y5QI":{
                    "usage_key":"block_component_usage_id",
                    "category":"html",
                    "data_block_ids: {
                        "display_name": 1,
                        "content": 10
                    },
                    "status": {
                        "applied": false,
                        "approved": false,
                        "last_fetched": null,
                        "approved_by": edx
                    },
                    "data": {
                        "display_name":"Html Text",
                        "content":"<h1>Hello World<h1/>"
                    }
                },
            }
            'base_course_outline': {
                "7VLKTTPX1ZUJI8KA":{
                    "usage_key":"base_block_component_usage_id",
                    "category":"problem",
                    "data":{
                        "display_name":"",
                        "content":""
                    }
                },
                "B36BXKA90A56Y5QI":{
                    "usage_key":"base_block_component_usage_id",
                    "category":"html",
                    "data": {
                        "display_name":"",
                        "content":""
                    }
                },
            }
        }
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        usage_key = kwargs.get('unit_key')
        block_location = UsageKey.from_string(usage_key)

        unit = modulestore().get_item(block_location)

        unit_data, base_unit_data, = get_outline_unit_to_components(unit)
        if unit_data and base_unit_data:
            key, base_key = list(unit_data.keys())[0], list(base_unit_data.keys())[0]
            unit_data, base_unit_data = unit_data[key]['children'], base_unit_data[base_key]['children']

        data = {
            'components_data': unit_data,
            'base_components_data': base_unit_data,
        }

        return Response(data, status=status.HTTP_200_OK)

class GetCoursesVersionInfo(generics.RetrieveAPIView):
    """
    API to get ids of user courses with their translated versions

    GET meta_translations/api/v0/versions
    Response:
    {
        {
            "base_course_key_1" : {
                "id": "base_course_key_1,
                "title": "Introduction To Computing (English base course)",
                "language": "en",
                "rerun": {
                    course_key_2: {
                        "id": "course_key_2",
                        "tilte": "Introduction To Computing(Urdu)",
                        "language": "ur",
                    },
                    course_key_3: {
                        "id": "course_key_3",
                        "tilte": "Introduction To Computing(French)",
                        "language": "fr",
                    }
                }
            }
        }
    }

    For Superusers Only:
        Optional parameter can be added to filter out own created courses instead of getting all courses.
        GET meta_translations/api/v0/versions?admin_created_courses=true
    """
    permission_classes = (permissions.IsAuthenticated,)

    def _course_version_format(self, course_key):
        course = get_course_by_id(course_key)
        base_course_obj = {
            'id': str(course.id),
            'title': str(course.display_name),
            'language': course.language,
            'rerun': get_courses_of_base_course(course.id)
        }
        return str(course.id), base_course_obj

    def _get_course_ids_list(self, request, admin_created_courses=False):
        """
        if admin_created_courses is set -> return course ids only for courses created by admin.
        otherwise -> return user accessible courses i.e
            For admin users and staff users -> return all courses.
            For normal users -> return user created courses + courses on which user is added in Course Team.
        """
        # courses accessible to users. For staff/superusers all courses will be returned.
        user_courses, _ = get_courses_accessible_to_user(request)

        # option only for superuser to filter out own created courses.
        if request.user.is_superuser and admin_created_courses:
            course_keys = []
            for course in user_courses:
                role = CourseStaffRole(course.id)
                if role.has_user(request.user, check_user_activation=False):
                    course_keys.append(course.id)
        else:
            course_keys = [course.id for course in user_courses]

        return course_keys


    def get(self, request, *args, **kwargs):
        admin_created_courses = False
        if request.user.is_superuser:
            admin_created_courses = self.request.GET.get('admin_created_courses', False)

        course_keys = self._get_course_ids_list(request, str(admin_created_courses).upper()=='TRUE')
        translated_courses = CourseTranslation.objects.filter(base_course_id__in=course_keys, outdated=False)
        base_course_keys = [translated_course.base_course_id for translated_course in translated_courses]
        base_course_keys = list(set(base_course_keys))
        data = [self._course_version_format(key) for key in base_course_keys]
        json_data = dict(data)
        return Response(json_data, status=status.HTTP_200_OK)

class ApproveAPIView(generics.UpdateAPIView):
    """
    API to update Approve flag of wiki_translations
    Hit this URL: /meta_translations/api/v0/approve_translations/
    PUT API:
        Request:
        {
            block_ids = [
                '<block_id_1>',
                '<block_id_2>',
            ],
        }
        Response:
        {
            <block_id_1> : {
                "block_id": "<block_id_1>",
                "block_type": "chapter",
                "course_id": "<course_id>",
                "approved": true,
                "applied": true,
                "applied_version": 1,
                "applied_version_date": 'Jun 10, 2022, 5:19 a.m',
            },
            <block_id_2> : {
                "block_id": "<block_id_1>",
                "block_type": "sequential",
                "course_id": "<course_id>",
                "approved": true,
                "applied": true,
                "applied_version": 1,
                "applied_version_date": 'Jun 10, 2022, 5:19 a.m',
            }
        }
    
    """
    serializer_class = CourseBlockTranslationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self, block_ids):
        return CourseBlock.objects.filter(block_id__in=block_ids)

    def update(self, request):
        block_ids = request.data.get('block_ids', [])
        blocks = self.get_queryset(block_ids)
        json_data = {}
        for block in blocks:
            serializer = self.get_serializer(block, data={'approved': True})
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            data = serializer.data
            json_data[data['block_id']] = data
        return Response(json_data, status=status.HTTP_200_OK)

class TranslatedVersionRetrieveAPIView(generics.RetrieveAPIView):
    """
    An API view to get data of a specific version
    Hit this URL: /meta_translations/api/v0/translationd_version/<version_id>/
    GET API:
    {
        block_id: "<block_id>",
        date: "2022-06-10T04:06:30.131575Z",
        data: {display_name: "Introduction"},
        approved_by: 3,    
    } 
    """
    serializer_class = TranslationVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = TranslationVersion.objects.all()

class CouseBlockVersionUpdateView(generics.UpdateAPIView):
    """
    Serializer used to update transaltion version of a course block
    Hit this URL: /meta_translations/api/v0/apply_translated_version/(?P<block_id>.*?)
    PUT API:
        Request Data:
            {
                version_id: 7
            }
        Response:
            {
                "block_id": "<block_id>",
                "applied_translation": false,
                "applied_version": 9
            }
    """
    lookup_field = 'block_id'
    serializer_class = CourseBlockVersionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = CourseBlock.objects.all()

class MetaCoursesListAPIView(generics.ListAPIView):
    """
    An API view to retreive transalted courses and their base course
    Hit this URL: http://localhost:18010/meta_translations/api/v0/meta_courses
    GET API:
        Response:
            [
                {
                    "course_id": "<course_id>",
                    "base_course_id": "<base_course_id>",
                    "outdated": false,
                    "course_lang": "fr",
                    "course_name": "Testing Course Translated",
                    "base_course_lang": "en",
                    "base_course_name": "Testing Course"
                },
                ...
            ]
    """
    pagination_class = None
    serializer_class = MetaCoursesSerializer
    queryset = CourseTranslation.objects.filter(outdated=False)

class MetaCoursesRetrieveAPIView(generics.RetrieveAPIView):
    """
    An API view to retreive transalted course and their base course
    Hit this URL: http://localhost:18010/meta_translations/api/v0/meta_courses/<course_id>
    GET API:
        Response:
            {
                "course_id": "<course_id>",
                "base_course_id": "<base_course_id>",
                "outdated": false,
                "course_lang": "fr",
                "course_name": "Testing Course Translated",
                "base_course_lang": "en",
                "base_course_name": "Testing Course"
            },
    """
    lookup_field = 'course_id'
    serializer_class = MetaCoursesSerializer
    queryset = CourseTranslation.objects.filter(outdated=False)

class MetaCourseTranslationsAPIView(generics.ListAPIView):
    """
    An API view to get data of course blocks with wiki translations
    Hit this URL: meta_translations/api/v0/meta_course_translations?course_id=(?P<block_id>.*?)
    GET API:
        Response:
            {
                "next": null,
                "previous": null,
                "count": 2,
                "num_pages": 1,
                "current_page": 1,
                "start": 0,
                "data": [
                    {
                        "block_id": "<block_id>",
                        "block_type": "chapter",
                        "base_data": {
                            "display_name": "Introduction"
                        },
                        "is_translated": true,
                        "is_parsed_block": false,
                        "group_url": "<redirect_url_to_meta_server>"
                    },
                    ...
                ]
            }
    """
    serializer_class = MetaCourseTranslationSerializer

    def get_queryset(self):
        """
        Filter course blocks
        Query Parameters:
            course_id: filter by course_id
            block_types: filter by block_types i.e "chapter+sequential+vertical+html+video"
            translations: filter by translated flag i.e ('all', 'translated', 'untranslated')
        """
        filters = {}
        course_id = self.request.GET.get('course_id', None)
        if course_id:
            filters['course_id'] = course_id.replace(' ', '+')
        
        block_types = self.request.GET.get('block_types', 'all')
        if block_types != 'all':
            filters['block_type__in'] = block_types.split()
        
        translations = self.request.GET.get('translations', 'all')
        if translations == 'translated':
            filters['translated'] = True
        elif translations == 'untranslated':
            filters['translated'] = False
        
        return CourseBlock.objects.filter(deleted=False, direction_flag=CourseBlock._DESTINATION, **filters)
