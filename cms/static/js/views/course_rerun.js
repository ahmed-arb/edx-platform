define(['domReady', 'jquery', 'underscore', 'js/views/utils/create_course_utils',
    'common/js/components/utils/view_utils', 'edx-ui-toolkit/js/utils/html-utils'],
    function(domReady, $, _, CreateCourseUtilsFactory, ViewUtils, HtmlUtils) {
        'use strict';
        var CreateCourseUtils = new CreateCourseUtilsFactory({
            name: '.rerun-course-name',
            org: '.rerun-course-org',
            number: '.rerun-course-number',
            run: '.rerun-course-run',
            language: '.rerun-course-language',
            rerun_type: '.field-radio',
            save: '.rerun-course-save',
            errorWrapper: '.wrapper-error',
            errorMessage: '#course_rerun_error',
            tipError: 'span.tip-error',
            error: '.error',
            allowUnicode: '.allow-unicode-course-id'
        }, {
            shown: 'is-shown',
            showing: 'is-showing',
            hiding: 'is-hidden',
            disabled: 'is-disabled',
            error: 'error'
        });

        var saveRerunCourse = function(e) {
            var courseInfo;
            e.preventDefault();

            if (CreateCourseUtils.hasInvalidRequiredFields()) {
                return;
            }

            var $newCourseForm = $(this).closest('#rerun-course-form');
            var display_name = $newCourseForm.find('.rerun-course-name').val();
            var org = $newCourseForm.find('.rerun-course-org').val();
            var number = $newCourseForm.find('.rerun-course-number').val();
            var run = $newCourseForm.find('.rerun-course-run').val();
            var language = $newCourseForm.find('.rerun-course-language').val();
            var rerun_type = $newCourseForm.find('.field-radio:checked').val();

            courseInfo = {
                source_course_key: source_course_key,
                org: org,
                number: number,
                display_name: display_name,
                run: run,
                translated_rerun: rerun_type=="translated" ? true : false
            };

            if (rerun_type == 'translated'){
                courseInfo.language = language
            }

            analytics.track('Reran a Course', courseInfo); // eslint-disable-line no-undef
            CreateCourseUtils.create(courseInfo, function(errorMessage) {
                $('.wrapper-error').addClass('is-shown').removeClass('is-hidden');
                $('#course_rerun_error').html(HtmlUtils.joinHtml(HtmlUtils.HTML('<p>'), errorMessage, HtmlUtils.HTML('</p>')).toString()); // eslint-disable-line max-len
                $('.rerun-course-save').addClass('is-disabled').attr('aria-disabled', true)
                .removeClass('is-processing')
                .text(gettext('Create Re-run'));
                $('.action-cancel').removeClass('is-hidden');
            });

            // Go into creating re-run state
            $('.rerun-course-save').addClass('is-disabled').attr('aria-disabled', true)
            .addClass('is-processing')
            .html(HtmlUtils.joinHtml(HtmlUtils.HTML('<span class="icon fa fa-refresh fa-spin" aria-hidden="true"></span>'), gettext('Processing Re-run Request')).toString()); // eslint-disable-line max-len
            $('.action-cancel').addClass('is-hidden');
        };

        var cancelRerunCourse = function(e) {
            e.preventDefault();
            // Clear out existing fields and errors
            $('.rerun-course-run').val('');
            $('#course_rerun_error').html('');
            $('wrapper-error').removeClass('is-shown').addClass('is-hidden');
            $('.rerun-course-save').off('click');
            ViewUtils.redirect('/course/');
        };

        var onReady = function() {
            var $cancelButton = $('.rerun-course-cancel');
            var $courseRun = $('.rerun-course-run');
            var $basicRerunTranslation = $('.field-radio');
            var languageFilter = $('#field-course-language');

            $courseRun.focus().select();
            $('.rerun-course-save').on('click', saveRerunCourse);
            $cancelButton.bind('click', cancelRerunCourse);
            $('.cancel-button').bind('click', cancelRerunCourse);

            $basicRerunTranslation.on('change', function () {
                (this.id == 'basic-rerun') ?
                    languageFilter.slideUp()
                :
                    languageFilter.slideDown()
                ;
            });
            $("#basic-rerun").prop("checked", true);
            languageFilter.slideUp();
            CreateCourseUtils.configureHandlers();
        };

        domReady(onReady);

        // Return these functions so that they can be tested
        return {
            saveRerunCourse: saveRerunCourse,
            cancelRerunCourse: cancelRerunCourse,
            onReady: onReady
        };
    });
