"""
WE'RE USING MIGRATIONS!

If you make changes to this model, be sure to create an appropriate migration
file and check it in at the same time as your model changes. To do that,

1. Go to the edx-platform dir
2. ./manage.py schemamigration admin_report_task --auto description_of_your_change
3. Add the migration file created in edx-platform/lms/djangoapps/admin_report_task/migrations/


ASSUMPTIONS: modules have unique IDs, even across different module_types

"""
import json
import logging
from uuid import uuid4

from django.contrib.auth.models import User  # lint-amnesty, pylint: disable=imported-auth-user
from django.db import models, transaction
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

logger = logging.getLogger(__name__)

# define custom states used by AdminReportTask
QUEUING = 'QUEUING'
PROGRESS = 'PROGRESS'
TASK_INPUT_LENGTH = 10000


@python_2_unicode_compatible
class AdminReportTask(models.Model):
    """
    Stores information about background tasks that have been submitted to
    perform work by an instructor (or course staff).
    Examples include grading and rescoring.

    `task_type` identifies the kind of task being performed, e.g. rescoring.
    `course_id` uses the multiple course run's id to identify the course.
    `task_key` stores relevant input arguments encoded into key value for testing to see
           if the task is already running (together with task_type and course_id).
    `task_input` stores input arguments as JSON-serialized dict, for reporting purposes.
        Examples include url of problem being rescored, id of student if only one student being rescored.

    `task_id` stores the id used by celery for the background task.
    `task_state` stores the last known state of the celery task
    `task_output` stores the output of the celery task.
        Format is a JSON-serialized dict.  Content varies by task_type and task_state.

    `requester` stores id of user who submitted the task
    `created` stores date that entry was first created
    `updated` stores date that entry was last modified

    .. no_pii:
    """
    class Meta:
        app_label = "admin_dashboard"

    task_type = models.CharField(max_length=50, db_index=True)
    course_id = models.TextField()
    task_key = models.CharField(max_length=255, db_index=True)
    task_input = models.TextField()
    task_id = models.CharField(max_length=255, db_index=True)  # max_length from celery_taskmeta
    task_state = models.CharField(max_length=50, null=True, db_index=True)  # max_length from celery_taskmeta
    task_output = models.CharField(max_length=1024, null=True)
    requester = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    subtasks = models.TextField(blank=True)  # JSON dictionary

    def __repr__(self):
        return 'InstructorTask<{!r}>'.format({
            'task_type': self.task_type,
            'course_id': self.course_id,
            'task_input': self.task_input,
            'task_id': self.task_id,
            'task_state': self.task_state,
            'task_output': self.task_output,
        })

    def __str__(self):
        return str(repr(self))

    @classmethod
    def create(cls, course_id, task_type, task_key, task_input, requester):
        """
        Create an instance of InstructorTask.
        """
        # create the task_id here, and pass it into celery:
        task_id = str(uuid4())
        json_task_input = json.dumps(task_input)

        # check length of task_input, and return an exception if it's too long
        if len(json_task_input) > TASK_INPUT_LENGTH:
            logger.error(
                'Task input longer than: `%s` for `%s` of course: `%s`',
                TASK_INPUT_LENGTH,
                task_type,
                course_id
            )
            error_msg = _('An error has occurred. Task was not created.')
            raise AttributeError(error_msg)

        # create the task, then save it:
        admin_report_task = cls(
            course_id=course_id,
            task_type=task_type,
            task_id=task_id,
            task_key=task_key,
            task_input=json_task_input,
            task_state=QUEUING,
            requester=requester
        )
        admin_report_task.save_now()

        return admin_report_task

    @transaction.atomic
    def save_now(self):
        """
        Writes InstructorTask immediately, ensuring the transaction is committed.
        """
        self.save()

    @staticmethod
    def create_output_for_success(returned_result):
        """
        Converts successful result to output format.

        Raises a ValueError exception if the output is too long.
        """
        # In future, there should be a check here that the resulting JSON
        # will fit in the column.  In the meantime, just return an exception.
        json_output = json.dumps(returned_result)
        if len(json_output) > 1023:
            raise ValueError(f"Length of task output is too long: {json_output}")
        return json_output

    @staticmethod
    def create_output_for_failure(exception, traceback_string):
        """
        Converts failed result information to output format.

        Traceback information is truncated or not included if it would result in an output string
        that would not fit in the database.  If the output is still too long, then the
        exception message is also truncated.

        Truncation is indicated by adding "..." to the end of the value.
        """
        tag = '...'
        task_progress = {'exception': type(exception).__name__, 'message': str(exception)}
        if traceback_string is not None:
            # truncate any traceback that goes into the InstructorTask model:
            task_progress['traceback'] = traceback_string
        json_output = json.dumps(task_progress)
        # if the resulting output is too long, then first shorten the
        # traceback, and then the message, until it fits.
        too_long = len(json_output) - 1023
        if too_long > 0:
            if traceback_string is not None:
                if too_long >= len(traceback_string) - len(tag):
                    # remove the traceback entry entirely (so no key or value)
                    del task_progress['traceback']
                    too_long -= (len(traceback_string) + len('traceback'))
                else:
                    # truncate the traceback:
                    task_progress['traceback'] = traceback_string[:-(too_long + len(tag))] + tag
                    too_long = 0
            if too_long > 0:
                # we need to shorten the message:
                task_progress['message'] = task_progress['message'][:-(too_long + len(tag))] + tag
            json_output = json.dumps(task_progress)
        return json_output

    @staticmethod
    def create_output_for_revoked():
        """Creates standard message to store in output format for revoked tasks."""
        return json.dumps({'message': 'Task revoked before running'})
