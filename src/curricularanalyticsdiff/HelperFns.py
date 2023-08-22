import curricularanalytics as ca
from typing import List
from curricularanalytics import Course, Curriculum
from curricularanalytics.GraphAlgs import all_paths


# def course_match(course1_name: str, course2_name: str):
#    # TODO
#    return True


# def course_find(course_name: str, alternate_names: Matrix):
#    # TODO
#    return True


"""
    prereq_print(prereqs::List[String])
Return a string representing the names of all courses in the `prereqs` set. 

Usually only used for prereqs, hence the name. It can be used with any normal set of courses.
"""


def prereq_print(prereqs: List[str]) -> str:
    str = " "
    for prereq in prereqs:
        str = str + prereq + " "
    return str


"""
    get_course_prereqs(course: Course, curriculum: Curriculum)
Return a vector containing the courses that are prerequisites of `course`  in `curriculum`.
"""


def get_course_prereqs(course: Course, curriculum: Curriculum) -> List[Course]:
    # get all the prereqs
    course_prereqs: List[Course] = []
    for key in course.requisites:
        course = curriculum.course_from_id(key)
        course_prereqs.append(course)
    return course_prereqs


"""
    course_from_name(course_name: str, curriculum: Curriculum)

Return the course object with the name `course name` in the `curriculum`. 
In newer versions (since 0.1.5) this checks for a match with course prefix with course number following the UCSD format of "prefix num"

Serves as a human-readable alternative to `course_from_id` in the main Curricular Analytics package.
"""


def course_from_name(course_name: str, curriculum: Curriculum) -> Course:
    for c in curriculum.courses:
        compound_name = c.prefix + " " + c.num
        if compound_name == course_name and compound_name != " ":
            return c
    for c in curriculum.courses:
        if c.name == course_name:
            return c


"""
    pretty_print_course_names(courses::List[str])
Print course names prettily to console.

`courses` should be a vector of course names for this to work correctly.
"""


def pretty_print_course_names(courses: List[str]):
    # for course in courses:
    #    print(Crayon(reset=true), "$(course)➡️")
    # end
    # print(Crayon(reset=true), " \n")
    return True
    # TODO


"""
    courses_to_course_names(courses: List[Course])
Return an array of the course names corresponding to the given course objects in `courses` (should be a vector of course objects).
"""


def courses_to_course_names(courses: List[Course]):
    course_names: List[str] = []
    for course in courses:
        course_names.append(course.name)
    return course_names
    # TODO consider the prefix num stuff


"""
    courses_that_depend_on_me(course_me:Course, curriculum:Curriculum)
Return an array of courses that represent the first level of `course_me`'s unblocked field in `curriculum` (as defined by Curricular Analytics).

That is the list of courses that explicitly list `course_me` as a prerequisite. Includes co-requisites.
"""


def courses_that_depend_on_me(
    course_me: Course, curriculum: Curriculum
) -> List[Course]:
    # me is the course
    courses_that_depend_on_me: List[Course] = []
    # look through all courses in curriculum. if one of them lists me as a prereq, add them to the list
    for course in curriculum.courses:
        # look through the courses prerequisite
        for key in course.requisites:
            # the key is what matters, it is the id of the course in the curriculum
            if (
                key == course_me.id
            ):  # let's skip co-reqs for now... interesting to see if this matters later. It does! see MATH 20B of BE25 in the sample data
                courses_that_depend_on_me.append(course)

    return courses_that_depend_on_me


"""
    blocking_factor_investigator(course_me:Course, curriculum:Curriculum)
Return the list of courses that comprise `course_me`'s unblocked field (as defined by Curricular Analytics).
"""


def blocking_factor_investigator(
    course_me: Course, curriculum: Curriculum
) -> List[Course]:
    # this should:
    # check all courses to make a list of courses that consider this one a prereq
    # then for each of those find which courses deem that course a prereq
    # repeat until the list of courses that consider a given course a prereq is empty.
    unblocked_field = courses_that_depend_on_me(course_me, curriculum)
    if len(unblocked_field) != 0:
        # if theres courses that depend on my current course, find the immediately unblocked field of each of those courses
        # and add it to courses_that_depend_on_me
        for course_A in unblocked_field:
            courses_that_depend_on_course_A = courses_that_depend_on_me(
                course_A, curriculum
            )
            if len(courses_that_depend_on_course_A) != 0:
                for course in courses_that_depend_on_course_A:
                    if not (course in unblocked_field):  # avoid duplicates
                        unblocked_field.append(course)
    return unblocked_field


"""
    delay_factor_investigator(course_me:Course, curriculum:Curriculum)
Return a list representing a course path in `curriculum` passing through `course_me` with length equal to 
`course_me`'s delay factor. It is not *always* the same path as the one highlighted in the visualization package.
"""


def delay_factor_investigator(
    course_me: Course, curriculum: Curriculum
) -> List[Course]:
    # this is harder because we need to find the longest path
    # for each course in my unblocked field, calculate the longest path from a sink up to them that includes me
    my_unblocked_field = blocking_factor_investigator(course_me, curriculum)
    delay_factor_path: List[Course] = []
    # if my unblocked field is empty, find the longest path to me
    if len(my_unblocked_field) == 0:
        # call longest path to me with no filter
        delay_factor_path = longest_path_to_me(course_me, curriculum, course_me, False)
    else:
        # select only the sink nodes of my unblocked field. this is bad for time complexity, though
        sinks_in_my_u_field = filter(
            lambda x: len(courses_that_depend_on_me(x, curriculum)) == 0,
            my_unblocked_field,
        )

        # for each of the sinks, calculate longest path to them, that passes through me
        longest_path_through_me: List = []  # TODO get a type
        longest_length_through_me = 0
        for sink in sinks_in_my_u_field:
            # NOTE: this will unfortunately produce the longest path stemming from me, not the whole path. *shrug for now*
            path = longest_path_to_me(sink, curriculum, course_me, True)
            if len(path) > longest_length_through_me:
                longest_length_through_me = len(path)
                longest_path_through_me = path

        # now that you have the longest path stemming from me,
        # find the longest path to me and put em together. They will unfortunately include me twice, so make sure to remove me from one of them
        longest_up_to_me = longest_path_to_me(course_me, curriculum, course_me, False)
        longest_up_to_me.pop()
        for course in longest_up_to_me:
            delay_factor_path.append(course)
        for course in longest_path_through_me:
            delay_factor_path.append(course)
    return delay_factor_path


"""
    centrality_investigator(course_me:Course, curriculum:Curriculum)
Return a list of lists containg the paths that make up the centrality of `course_me` in `curriculum`.

Each list is one such path.
"""


def centrality_investigator(
    course_me: Course, curriculum: Curriculum
) -> List[List[Course]]:
    # this will return the paths that make up the centrality of a course
    g = curriculum.graph
    # TODO: find out why I used this method of getting the course as opposed to course_from_name
    # course = course_me.vertex_id[curriculum.id]
    course = course_from_name(course_me.name, curriculum)
    centrality_paths: List[List[Course]] = []
    for path in all_paths(g):
        # stole the conditions from the CurricularAnalytics.jl repo
        # pray that the course.id thing works here too, from CurricularAnalytics
        if (
            course.id in path
            and len(path) > 2
            and path[0] != course.id
            and path[-1] != course.id
        ):
            # convert this path to courses
            course_path: List[Course] = []
            for id in path:
                course_path.append(
                    curriculum.courses[id - 1]
                )  # -1 since we start counting at 1 but python starts at 0
            # then add this path to the collection of paths
            centrality_paths.append(course_path)
    return centrality_paths


"""
    longest_path_to_me(course_me:Course, curriculum:Curriculum, filter_course:Course, filter:Bool=False)
Returns the longest path in `curriculum` up to `course_me`. 

If the `filter` option is enabled, the aforementioned path is one that contains `filter_course`.
"""


def longest_path_to_me(
    course_me: Course,
    curriculum: Curriculum,
    filter_course: Course,
    filter: bool = False,
) -> List[Course]:
    # for each prereq of mine find the longest path up to that course
    longest_path_to_course_me: List[Course] = []
    longest_paths_to_me: List = []  # TODO: find this type
    for key in course_me.requisites:
        # if (value == pre) # reconsider if coreqs count here *shrug*
        longest_path_to_prereq = longest_path_to_me(
            curriculum.course_from_id(key), curriculum, filter_course, filter
        )
        longest_paths_to_me.append(longest_path_to_prereq)
        # end
    # compare the lengths, filter by the ones that contain the filter course if needed
    if filter:
        # choose the longest path length that contains filter course
        length_of_longest_path = 0
        for array in longest_paths_to_me:
            if len(array) > length_of_longest_path and filter_course in array:
                longest_path_to_course_me = array
                length_of_longest_path = len(array)
    else:
        # choose the longest path
        length_of_longest_path = 0
        for array in longest_paths_to_me:
            if len(array) > length_of_longest_path:
                longest_path_to_course_me = array
                length_of_longest_path = len(array)
    # add myself to the chosen longest path and return that
    longest_path_to_course_me.append(course_me)
    return longest_path_to_course_me


"""
    snippet(course:Course, curriculum:Curriculum)
Returns a sub-curriculum of the original including only the courses that compose `course`'s centrality paths
"""


def snippet(course: Course, curriculum: Curriculum):
    # this is the brain-dead way of doing this
    centrality_paths = centrality_investigator(course, curriculum)
    courses: set = set()
    extra_courses: set = set()
    centrality_courses: set = set()
    for path in centrality_paths:
        centrality_courses.union(path)
    for c in centrality_courses:
        extra_courses.union(set(get_course_prereqs(c, curriculum)))
    for c in centrality_courses:
        courses.append(c)
    for c in extra_courses:
        courses.append(c)
    return Curriculum("$(course.name) snippet", list(courses))
