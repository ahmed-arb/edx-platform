import React from "react";

import Subsections from "./Subsections";
import Accordion from "./Accordion";

function Sections(props) {
  const { base_course_outline, course_outline } = props.courseOutline;

  return (
    <div className="translation-frame">
      {
        Object.keys(base_course_outline)
        .map(section_id => {
          const baseTitle = base_course_outline[section_id].data.display_name;
          const rerunTitle = course_outline[section_id].data.display_name;

          return (
            <Accordion
              addClass="sections"
              key={section_id}
              baseTitle={baseTitle}
              section_id={section_id}
              rerunTitle={rerunTitle}
              pageUrl={base_course_outline[section_id].links.page_url}
              pageGroupUrl={course_outline[section_id].links.page_group_url}
              usageKey={course_outline[section_id].usage_key}
              approved={course_outline[section_id].status.approved}
              versionStatus={course_outline[section_id].version_status}
              destinationFlag={course_outline[section_id].status.destination_flag}
              isFullyTranslated={course_outline[section_id].status.is_fully_translated}
              {...props}
            >
              <Subsections
                section_id={section_id}
                baseCourseSubsections={base_course_outline[section_id].children}
                rerunCourseSubsections={course_outline[section_id].children}
                {...props}
              />
            </Accordion>
          )
        })
      }
    </div>
  );
}

export default Sections;
