import curricularanalytics as ca
from typing import List
from curricularanalytics import Course, Curriculum, Requisite
import curricularanalyticsdiff.HelperFns as hf
import copy

## WHAT IF:
# =
# I add a course?
# I remove a course?
# I add a prereq?
# I remove a prereq?
# =#
# @enum Edit_Type add del

# What if I add a course?
"""
    add_course(course_name, curr, credit_hours, prereqs, dependencies)
Return a copy of `curr` where a new course with the provided information has been added.

# Arguments
- `course_name:str`: The name of the course to add.
- `curr:Curriculum`: The curriculum to add a course to.
- `credit_hours:float`: How many credit hours the new course is worth.
- `prereqs:Dict`: The names of the prerequisites for the new course and their requisite type.
- `dependencies:Dict`: The names of the courses that would have the new course as a prerequisite and the requisite type.
"""


def add_course(
    course_name: str,
    curr: Curriculum,
    credit_hours: float,
    prereqs: dict,
    dependencies: dict,
) -> Curriculum:
    ## create the course in the curricular analytics sense
    new_course = Course(course_name, credit_hours)
    modded_curric = copy.deepcopy(curr)
    ## hook it up to the curriculum
    # loop through the names of its prereqs and find them in modded_curric (so we don't alter the original)
    for prereq in prereqs:
        prereq_course = hf.course_from_name(prereq, modded_curric)
        if prereq_course is None:
            raise ValueError(
                "I'm sorry, we couldn't find your requested prerequisite in the given curriculum. Are you sure its name matched the one in the file exactly?"
            )

        # add_requisite!(prereq_course, new_course, req_type)
        req_type = prereqs[prereq]
        new_course.add_requisite(prereq_course, req_type)
    # loop through the names of its dependencies and find them in modded_curric
    for dep in dependencies:
        dependent_course = hf.course_from_name(dep, modded_curric)
        if dependent_course is None:
            raise ValueError(
                "I'm sorry, we couldn't find your requested dependent course in the given curriculum. Are you sure its name matched the one in the file exactly?"
            )

        # add_requisite!(new_course, dependent_course, type)
        req_type = dependencies[dep]
        dependent_course.add_requisite(new_course, req_type)

    ## make a new curriculum after modifying these courses
    course_list = modded_curric.courses
    # push!(course_list, new_course)
    course_list.append(new_course)

    return Curriculum("Proposed Curriculum", course_list, system_type=curr.system_type)


# What if I remove a course?
"""
    remove_course(course_name:str, curr:Curriculum)
Return a copy of `curr` where the course with name `course_name` has been removed.

It is removed from all of the prerequisite chains it was in.
"""


def remove_course(course_name: str, curr: Curriculum) -> Curriculum:
    modded_curric = copy.deepcopy(curr)
    course = hf.course_from_name(course_name, modded_curric)
    if course is None:
        raise ValueError(
            "I'm sorry, we couldn't find your requested course in the given curriculum. Are you sure its name matched the one in the file exactly?"
        )

    # unhook it from the curriculum
    # loop through its dependents and unhook
    dependents = hf.courses_that_depend_on_me(course, modded_curric)

    for dep in dependents:
        # delete_requisite!(course, dep)
        dep.delete_requisite(course)

    # technically we should unhook from the given course TOO
    for req_id in course.requisites:
        req = ca.course_from_id(modded_curric, req_id)
        # delete_requisite!(req, course)
        course.delete_prerquisite(req)

    # Make a new curriculum
    new_course_list: List[Course] = []
    for crs in modded_curric.courses:
        if crs != course:
            # push!(new_course_list, crs)
            new_course_list.append(crs)

    return Curriculum(
        "Proposed Curriculum", new_course_list, system_type=curr.system_type
    )


# What if I add a prereq to this course?
"""
    add_prereq(course_name:AbstracString, added_prereq:AbstracString, curr:Curriculum, reqtype:Requisite)
Return a copy of `curr` where the course with name `added_prereq` has been added as a requisite of type `reqtype` to the course with name `course_name`.
"""


def add_prereq(
    course_name: str, added_prereq: str, curr: Curriculum, req_type: Requisite
) -> Curriculum:
    modded_curric = copy.deepcopy(curr)

    target_course = hf.course_from_name(course_name, modded_curric)
    if target_course is None:
        raise ValueError(
            "I'm sorry, we couldn't find your requested course in the given curriculum. Are you sure its name matched the one in the file exactly?"
        )

    added_prq = hf.course_from_name(added_prereq, modded_curric)
    if added_prq is None:
        raise ValueError(
            "I'm sorry, we couldn't find your requested prerequisite in the given curriculum. Are you sure its name matched the one in the file exactly?"
        )

    # add_requisite!(added_prq, target_course, req_type)
    target_course.add_requisite(added_prq, req_type)

    return Curriculum(
        "Proposed Curriculum", modded_curric.courses, system_type=curr.system_type
    )


# What if I remove to_remove from course_name?
"""
    remove_prereq(course_name:str, to_remove:str, curr:Curriculum)
Return a copy of `curr` where the course with name `to_remove` has been removed as a prerequisite of the course with name `course_name`.
"""


def remove_prereq(course_name: str, to_remove: str, curr: Curriculum) -> Curriculum:
    modded_curric = copy.deepcopy(curr)

    course = hf.course_from_name(course_name, modded_curric)
    if course is None:
        raise ValueError(
            "I'm sorry, we couldn't find your requested course in the given curriculum. Are you sure its name matched the one in the file exactly?"
        )

    to_remove_course = hf.course_from_name(to_remove, modded_curric)
    if to_remove_course is None:
        raise ValueError(
            "I'm sorry, we couldn't find your requested prerequisite in the given curriculum. Are you sure its name matched the one in the file exactly?"
        )

    # delete_requisite!(to_remove_course, course)
    course.delete_requisite(to_remove_course)
    return Curriculum(
        "Proposed Curriculum", modded_curric.courses, system_type=curr.system_type
    )
