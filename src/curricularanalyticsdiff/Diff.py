import curricularanalytics as ca
from typing import List
from curricularanalytics import Course, Curriculum
from curricularanalytics.GraphAlgs import all_paths
import curricularanalyticsdiff.HelperFns as hf


"""
    course_diff_for_unmatched_course(course, curriculum, c1)
Analyze differences in the key curriculum metrics for a course that has no match in the other curriculum.

# Arguments
- `course:Course`: the course in question.
- `curriculum:Curriculum`: the curriculum that `course` exists in.
- `c1:bool`: indicates if the curriculum the course with no match is the first or the second curriculum.
"""


def course_diff_for_unmatched_course(course: Course, curriculum: Curriculum, c1: bool):
    results = dict()
    contribution = dict(
        {
            "complexity": -course.metrics["complexity"]
            if c1
            else course.metrics["complexity"],
            "centrality": -course.metrics["centrality"]
            if c1
            else course.metrics["centrality"],
            "blocking factor": -course.metrics["blocking factor"]
            if c1
            else course.metrics["blocking factor"],
            "delay factor": -course.metrics["delay factor"]
            if c1
            else course.metrics["delay factor"],
        }
    )

    results["c1"] = c1
    results["contribution to curriculum differences"] = contribution
    results["complexity"] = course.metrics["complexity"]
    results["centrality"] = course.metrics["centrality"]
    results["prereqs"] = hf.courses_to_course_names(
        hf.get_course_prereqs(course, curriculum)
    )
    results["blocking factor"] = course.metrics["blocking factor"]
    results["delay factor"] = course.metrics["delay factor"]
    results


"""
    course_diff(course1:Course, course2:Course, curriculum1:Curriculum, curriculum2:Curriculum, deepdive:bool)

Analyze differences in the key curriculum metrics between `course1` in `curriculum1` and `course2` in `curriculum2`. 

# Arguments
- `course1:Course`: The first of the two courses to compare.
- `course2:Course`: The second of the two courses to compare.
- `curriculum1:Curriculum`: The curriculum that `course1` exists in.
- `curriculum2:Curriculum`: The curriculum that `course2` exists in.
- `deepdive:bool`: Determines whether or not it should stop upon finding no difference in the metric values. Defaults to true
"""


def course_diff(
    course1: Course,
    course2: Course,
    curriculum1: Curriculum,
    curriculum2: Curriculum,
    deep_dive: bool = True,
):
    # relevant_fields = filter(x ->
    #        x != :vertex_id &&
    #            x != :cross_listed &&
    #            x != :requisites &&
    #            x != :learning_outcomes &&
    #            x != :metrics &&
    #            x != :passrate &&
    #            x != :metadata,
    #    fieldnames(Course))

    # for field in relevant_fields
    #    field1 = getfield(course1, field)
    #    field2 = getfield(course2, field)
    #    if (field1 == field2)
    #        if (verbose)
    #            print(f"✅Course 1 and Course 2 have the same $field: $field1")
    #
    #    else:
    #        print(f"❌Course 1 has $(field): $field1 and Course 2 has $(field): $field2")
    #
    #
    # =#
    contribution = dict(
        {
            "complexity": 0.0,
            "centrality": 0.0,
            "blocking factor": 0.0,
            "delay factor": 0.0,
        }
    )

    # METRICS
    # complexity
    explanations_complexity = dict()
    explanations_complexity["course 1 score"] = course1.metrics["complexity"]
    explanations_complexity["course 2 score"] = course2.metrics["complexity"]
    if course1.metrics["complexity"] != course2.metrics["complexity"]:
        # print(f"❌Course 1 has complexity $(course1.metrics["complexity"]) and Course 2 has complexity $(course2.metrics["complexity"])")
        contribution["complexity"] = (
            course2.metrics["complexity"] - course1.metrics["complexity"]
        )

    # centrality
    explanations_centrality = dict()
    explanations_centrality["course 1 score"] = course1.metrics["centrality"]
    explanations_centrality["course 2 score"] = course2.metrics["centrality"]
    if not (
        course1.metrics["centrality"] == course2.metrics["centrality"] and not deep_dive
    ):
        # print(f"❌Course 1 has centrality $(course1.metrics["centrality"]) and Course 2 has centrality $(course2.metrics["centrality"])")
        contribution["centrality"] = (
            course2.metrics["centrality"] - course1.metrics["centrality"]
        )

        # run the investigator and then compare
        centrality_c1 = hf.centrality_investigator(course1, curriculum1)
        centrality_c2 = hf.centrality_investigator(course2, curriculum2)

        # turn those into course names
        # note that its an array of arrays so for each entry you have to convert to course names
        centrality_c1_set = set()
        centrality_c2_set = set()
        for path in centrality_c1:
            path_names = hf.courses_to_course_names(path)
            centrality_c1_set.add(path_names)
        for path in centrality_c2:
            path_names = hf.courses_to_course_names(path)
            centrality_c2_set.add(path_names)
        # set diff
        not_in_c2 = centrality_c1_set.difference(centrality_c2_set)
        not_in_c1 = centrality_c2_set.difference(centrality_c1_set)

        # analyse

        explanations_centrality["paths not in c2"] = list(not_in_c2)
        explanations_centrality["paths not in c1"] = list(not_in_c1)
        explanations_centrality["courses not in c2 paths"] = dict()
        explanations_centrality["courses not in c1 paths"] = dict()

        # TODO: consider explaining these differences, but they should be explainable by changes in the block and delay factors.
        # The only complication there is that these changes can be attributed to changes in the prereqs of those block and delay factors so theyre compounded. It's a lot harder
        # Would have to go through all the members of those paths and check each of those for changes. Could be.

        # To explain differences grab all the courses in the set of paths not in c2
        # check them against the matching courses in c2 looking for changes in prereqs
        # grab all the courses in the set of paths not in c1
        # check them against the matching courses in c1 looking for changes in prereqs

        # grab all the courses in the set of paths not in c2
        all_courses_not_in_c2 = []
        for path in not_in_c2:
            # this is a vector of AbstractString. look in each entry of that vector for course names
            for course in path:
                if not (course in all_courses_not_in_c2):
                    all_courses_not_in_c2.append(course)
        # check them against matching courses in c2 looking for different prereqs
        for course in all_courses_not_in_c2:
            c1 = hf.course_from_name(course, curriculum1)
            c2 = hf.course_from_name(course, curriculum2)
            # find their prerequisites
            prereqs_in_curr1 = set(
                hf.courses_to_course_names(hf.get_course_prereqs(c1, curriculum1))
            )

            prereqs_in_curr2 = (
                set()
                if c2 is None
                else set(
                    hf.courses_to_course_names(hf.get_course_prereqs(c2, curriculum2))
                )
            )
            # compare the prerequisites
            # lost prereqs are those that from c1 to c2 got dropped
            # gained prerqs are those that from c1 to c2 got added
            lost_prereqs = prereqs_in_curr1.difference(prereqs_in_curr2)
            gained_prereqs = prereqs_in_curr2.difference(prereqs_in_curr1)

            explanations_centrality["courses not in c2 paths"][course] = dict()
            explanations_centrality["courses not in c2 paths"][course][
                "lost prereqs"
            ] = list(lost_prereqs)
            explanations_centrality["courses not in c2 paths"][course][
                "gained prereqs"
            ] = list(gained_prereqs)

        # grab all the courses in the set of paths not in c1
        all_courses_not_in_c1 = []
        for path in not_in_c1:
            # this is a vector of AbstractString. look in each entry of that vector for course names
            for course in path:
                if not (course in all_courses_not_in_c1):
                    all_courses_not_in_c1.append(course)
        # check them against matching courses in c2 looking for different prereqs
        for course in all_courses_not_in_c1:
            c1 = hf.course_from_name(course, curriculum1)
            c2 = hf.course_from_name(course, curriculum2)
            # find their prerequisites
            prereqs_in_curr1 = (
                set()
                if c1 is None
                else set(
                    hf.courses_to_course_names(hf.get_course_prereqs(c1, curriculum1))
                )
            )
            prereqs_in_curr2 = set(
                hf.courses_to_course_names(hf.get_course_prereqs(c2, curriculum2))
            )
            # compare the prerequisites
            # lost prereqs are those that from c1 to c2 got dropped
            # gained prerqs are those that from c1 to c2 got added
            lost_prereqs = prereqs_in_curr1.difference(prereqs_in_curr2)
            gained_prereqs = prereqs_in_curr2.difference(prereqs_in_curr1)

            explanations_centrality["courses not in c1 paths"][course] = dict()
            explanations_centrality["courses not in c1 paths"][course][
                "lost prereqs"
            ] = list(lost_prereqs)
            explanations_centrality["courses not in c1 paths"][course][
                "gained prereqs"
            ] = list(gained_prereqs)

    # blocking factor
    explanations_blockingfactor = dict()
    explanations_blockingfactor["course 1 score"] = course1.metrics["blocking factor"]
    explanations_blockingfactor["course 2 score"] = course2.metrics["blocking factor"]
    if not (
        course1.metrics["blocking factor"] == course2.metrics["blocking factor"]
        and not deep_dive
    ):
        # print(f"❌Course 1 has blocking factor $(course1.metrics["blocking factor"]) and Course 2 has blocking factor $(course2.metrics["blocking factor"])")
        contribution["blocking factor"] = (
            course2.metrics["blocking factor"] - course1.metrics["blocking factor"]
        )

        # since they have different blocking factors, investigate why and get a set of blocking factors
        unblocked_field_course_1 = hf.blocking_factor_investigator(course1, curriculum1)
        unblocked_field_course_2 = hf.blocking_factor_investigator(course2, curriculum2)
        unblocked_field_course_1_names = set(
            hf.courses_to_course_names(unblocked_field_course_1)
        )
        unblocked_field_course_2_names = set(
            hf.courses_to_course_names(unblocked_field_course_2)
        )
        # use setdiff to track which courses aren't in course 2's unblocked field and which aren't in course 1's unblocked field
        not_in_c2_unbl_field = unblocked_field_course_1_names.difference(
            unblocked_field_course_2_names
        )
        not_in_c1_unbl_field = unblocked_field_course_2_names.difference(
            unblocked_field_course_1_names
        )

        explanations_blockingfactor["length not in c2 ufield"] = len(
            not_in_c2_unbl_field
        )
        explanations_blockingfactor["not in c2 ufield"] = dict()
        if len(not_in_c2_unbl_field) != 0:
            # there are courses in c1's unblocked that aren't in course2s
            # FIND THE COURSES HERE THAT HAVE CHANGED THEIR PREREQS
            for course_name in not_in_c2_unbl_field:
                explanations_blockingfactor["not in c2 ufield"][course_name] = dict()
                # find course to match name in curriculum1 and curriculum2
                course_in_curr1 = hf.course_from_name(course_name, curriculum1)
                course_in_curr2 = hf.course_from_name(course_name, curriculum2)
                # and find c1 prereqs
                prereqs_in_curr1 = set(
                    hf.courses_to_course_names(
                        hf.get_course_prereqs(course_in_curr1, curriculum1)
                    )
                )
                if not course_in_curr2 is None:
                    # find their prerequisites
                    prereqs_in_curr2 = set(
                        hf.courses_to_course_names(
                            hf.get_course_prereqs(course_in_curr2, curriculum2)
                        )
                    )
                    # compare the prerequisites
                    # lost prereqs are those that from c1 to c2 got dropped
                    # gained prerqs are those that from c1 to c2 got added
                    lost_prereqs = prereqs_in_curr1.difference(prereqs_in_curr2)
                    gained_prereqs = prereqs_in_curr2.difference(prereqs_in_curr1)
                    explanations_blockingfactor["not in c2 ufield"][course_name][
                        "lost prereqs"
                    ] = list(lost_prereqs)
                    explanations_blockingfactor["not in c2 ufield"][course_name][
                        "gained prereqs"
                    ] = list(gained_prereqs)
                else:
                    # if there's no match in curriculum 2, then just say all the prereqs were lost and none were gained
                    explanations_blockingfactor["not in c2 ufield"][course_name][
                        "lost prereqs"
                    ] = hf.courses_to_course_names(
                        hf.get_course_prereqs(course_in_curr1, curriculum1)
                    )
                    explanations_blockingfactor["not in c2 ufield"][course_name][
                        "gained prereqs"
                    ] = []
                # check if the prereqs haven't changed. If they haven't changed, we need to find which of their prereqs did
                if (
                    len(
                        explanations_blockingfactor["not in c2 ufield"][course_name][
                            "lost prereqs"
                        ]
                    )
                    == 0
                    and len(
                        explanations_blockingfactor["not in c2 ufield"][course_name][
                            "gained prereqs"
                        ]
                    )
                    == 0
                ):
                    # find this course's prereqs and match them with any other courses in not_in_c2_unbl_field
                    # find this course's prereqs in curriculum 1
                    prereqs_in_curr1_set = set(prereqs_in_curr1)
                    # cross reference with the list of courses not in not_in_c2_unbl_field
                    not_in_c2_unbl_field_set = set(not_in_c2_unbl_field)

                    in_both = prereqs_in_curr1_set.intersection(
                        not_in_c2_unbl_field_set
                    )

                    explanations_blockingfactor["not in c2 ufield"][course_name][
                        "in_both"
                    ] = list(in_both)

                else:
                    explanations_blockingfactor["not in c2 ufield"][course_name][
                        "in_both"
                    ] = []
        explanations_blockingfactor["length not in c1 ufield"] = len(
            not_in_c1_unbl_field
        )
        explanations_blockingfactor["not in c1 ufield"] = dict()
        if len(not_in_c1_unbl_field) != 0:
            # there are courses in c2's unblocked that aren't in course1s
            # TODO: FIND THE COURSES HERE THAT HAVE CHANGED THEIR PREREQS
            for course_name in not_in_c1_unbl_field:
                explanations_blockingfactor["not in c1 ufield"][course_name] = dict()
                # find course to match name in curriculum1 and curriculum2
                course_in_curr1 = hf.course_from_name(course_name, curriculum1)
                course_in_curr2 = hf.course_from_name(course_name, curriculum2)
                # find prereqs in c2
                prereqs_in_curr2 = set(
                    hf.courses_to_course_names(
                        hf.get_course_prereqs(course_in_curr2, curriculum2)
                    )
                )
                if not course_in_curr1 is None:
                    # find their prerequisites
                    prereqs_in_curr1 = set(
                        hf.courses_to_course_names(
                            hf.get_course_prereqs(course_in_curr1, curriculum1)
                        )
                    )

                    # compare the prerequisites
                    lost_prereqs = prereqs_in_curr1.difference(prereqs_in_curr2)
                    gained_prereqs = prereqs_in_curr2.difference(prereqs_in_curr1)

                    explanations_blockingfactor["not in c1 ufield"][course_name][
                        "lost prereqs"
                    ] = list(lost_prereqs)
                    explanations_blockingfactor["not in c1 ufield"][course_name][
                        "gained prereqs"
                    ] = list(gained_prereqs)
                else:
                    # if there's no match in curriculum 2, then just say that all the prereqs have been gained and none were lost
                    explanations_blockingfactor["not in c1 ufield"][course_name][
                        "lost prereqs"
                    ] = []
                    explanations_blockingfactor["not in c1 ufield"][course_name][
                        "gained prereqs"
                    ] = hf.courses_to_course_names(
                        hf.get_course_prereqs(course_in_curr2, curriculum2)
                    )
                # check if the prereqs haven't changed. If they haven't changed, we need to find which of their prereqs did
                if (
                    len(
                        explanations_blockingfactor["not in c1 ufield"][course_name][
                            "lost prereqs"
                        ]
                    )
                    == 0
                    and len(
                        explanations_blockingfactor["not in c1 ufield"][course_name][
                            "gained prereqs"
                        ]
                    )
                    == 0
                ):
                    # find this course's prereqs and match them with any other courses in not_in_c1_unbl_field
                    # find this course's prereqs in curriculum 2
                    prereqs_in_curr2_set = set(prereqs_in_curr2)
                    # cross reference with the list of courses not in not_in_c1_unbl_field
                    not_in_c1_unbl_field_set = set(not_in_c1_unbl_field)

                    in_both = prereqs_in_curr2_set.intersection(
                        not_in_c1_unbl_field_set
                    )

                    explanations_blockingfactor["not in c1 ufield"][course_name][
                        "in_both"
                    ] = list(in_both)
                else:
                    explanations_blockingfactor["not in c1 ufield"][course_name][
                        "in_both"
                    ] = []
    # delay factor
    explanations_delayfactor = dict()
    explanations_delayfactor["course 1 score"] = course1.metrics["delay factor"]
    explanations_delayfactor["course 2 score"] = course2.metrics["delay factor"]
    if not (
        course1.metrics["delay factor"] == course2.metrics["delay factor"]
        and not deep_dive
    ):
        # print(f"❌Course 1 has delay factor $(course1.metrics["delay factor"]) and Course 2 has delay factor $(course2.metrics["delay factor"])")
        contribution["delay factor"] = (
            course2.metrics["delay factor"] - course1.metrics["delay factor"]
        )
        df_path_course_1 = hf.courses_to_course_names(
            hf.delay_factor_investigator(course1, curriculum1)
        )
        df_path_course_2 = hf.courses_to_course_names(
            hf.delay_factor_investigator(course2, curriculum2)
        )

        explanations_delayfactor["df path course 1"] = df_path_course_1
        explanations_delayfactor["df path course 2"] = df_path_course_2
        # explain why
        df_set_c1 = set(df_path_course_1)
        df_set_c2 = set(df_path_course_2)

        all_courses_in_paths = df_set_c1.union(df_set_c2)
        explanations_delayfactor["courses involved"] = dict()

        for course in all_courses_in_paths:
            explanations_delayfactor["courses involved"][course] = dict()
            # find course to match name in curriculum1 and curriculum2
            course_in_curr1 = hf.course_from_name(course, curriculum1)
            course_in_curr2 = hf.course_from_name(course, curriculum2)
            # find their prerequisites
            prereqs_in_curr1 = (
                set()
                if (course_in_curr1 is None)
                else set(
                    hf.courses_to_course_names(
                        hf.get_course_prereqs(course_in_curr1, curriculum1)
                    )
                )
            )

            prereqs_in_curr2 = (
                set()
                if course_in_curr2 is None
                else set(
                    hf.courses_to_course_names(
                        hf.get_course_prereqs(course_in_curr2, curriculum2)
                    )
                )
            )
            # compare the prerequisites
            # lost prereqs are those that from c1 to c2 got dropped
            # gained prerqs are those that from c1 to c2 got added
            lost_prereqs = prereqs_in_curr1.difference(prereqs_in_curr2)
            gained_prereqs = prereqs_in_curr2.difference(prereqs_in_curr1)
            explanations_delayfactor["courses involved"][course]["lost prereqs"] = list(
                lost_prereqs
            )
            explanations_delayfactor["courses involved"][course][
                "gained prereqs"
            ] = list(gained_prereqs)
    # requisites
    # collate all the prerequisite names from course 1
    course1_prereqs = set(
        hf.courses_to_course_names(hf.get_course_prereqs(course1, curriculum1))
    )
    course2_prereqs = set(
        hf.courses_to_course_names(hf.get_course_prereqs(course2, curriculum2))
    )

    explanations_prereqs = dict()
    lost_prereqs = course1_prereqs.difference(course2_prereqs)
    gained_prereqs = course2_prereqs.difference(course1_prereqs)
    explanations_prereqs["lost prereqs"] = list(lost_prereqs)
    explanations_prereqs["gained prereqs"] = list(gained_prereqs)

    return dict(
        {
            "c1 name": curriculum1.name,
            "c2 name": curriculum2.name,
            "contribution to curriculum differences": contribution,
            "complexity": explanations_complexity,
            "centrality": explanations_centrality,
            "blocking factor": explanations_blockingfactor,
            "delay factor": explanations_delayfactor,
            "prereqs": explanations_prereqs,
        }
    )


"""
    curricular_diff(curriculum1, curriculum2, verbose, redundants, redundants_file)

Analyze differences between two given curricula. 

Results should be interpreted as differences from `curriculum1` to `curriculum2`.

# Arguments
- `curriculum1:Curriculum`: The first curriculum to be compared.
- `curriculum2:Curriculum`: The second curriculum to be compared.
- `verbose:bool`: Whether or not the results should be verbose. If metrics all match up between curricula with verbose being False, we stop there. Defaults to False.
- `redundants:bool`: Whether or not diff will use redundant course names. Defaults to False.
- `redundants_file:String`: Path to a CSV file containing all the names that refer to the same course, like MATH 20F and MATH 18 at UCSD. Defaults to the empty string.
"""


def curricular_diff(
    curriculum1: Curriculum, curriculum2: Curriculum, verbose: bool = True
):
    # , redundants:bool=False, redundants_file:str=""
    # = using fieldnames instead of explicit names
    # relevant_fields = filter(x ->
    #        x != :courses &&
    #            x != :graph &&
    #            x != :learning_outcomes &&
    #            x != :learning_outcome_graph &&
    #            x != :course_learning_outcome_graph &&
    #            x != :metrics &&
    #            x != :metadata,
    #    fieldnames(Curriculum))

    # for field in relevant_fields
    #    field1 = getfield(curriculum1, field)
    #    field2 = getfield(curriculum2, field)
    #    if (field1 == field2)
    #        if (verbose)
    #            print(f"✅Curriculum 1 and Curriculum 2 have the same $field: $field1")
    #        end
    #    else:
    #        print(f"❌Curriculum 1 has $(field): $field1 and Curriculum 2 has $(field): $field2")
    #    end
    # end
    # =#
    # redundant_course_names = []
    # if (redundants):
    #    names = CSV.read(redundants_file)
    #    redundant_course_names = Matrix(names)
    # end
    # compare metrics
    try:
        ca.basic_metrics(curriculum1)
    finally:
        print("all good")
    try:
        ca.basic_metrics(curriculum2)
    finally:
        print("all good")
    all_results = dict()
    metrics_same = True
    # complexity and max complexity
    if curriculum1.metrics["complexity"][1] == curriculum2.metrics["complexity"][1]:
        if verbose:
            print(
                f"✅Curriculum 1 and Curriculum 2 have the same total complexity: {curriculum1.metrics['complexity'][1]}"
            )
    else:
        print(
            f"❌Curriculum 1 has a total complexity score of {curriculum1.metrics['complexity'][1]} and Curriculum2 has a total complexity score {curriculum2.metrics['complexity'][1]}"
        )
        metrics_same = False
    if curriculum1.metrics["max. complexity"] == curriculum2.metrics["max. complexity"]:
        if verbose:
            print(
                f"✅Curriculum 1 and Curriculum 2 have the same max complexity : {curriculum1.metrics['max. complexity']}"
            )
    else:
        print(
            f"❌Curriculum 1 has a max complexity of {curriculum1.metrics['max. complexity']} and Curriculum 2 has a max complexity of {curriculum2.metrics['max. complexity']}"
        )
        metrics_same = False
    # centrality and max centrality
    if curriculum1.metrics["centrality"][1] == curriculum2.metrics["centrality"][1]:
        if verbose:
            print(
                f"✅Curriculum 1 and Curriculum 2 have the same total centrality: {curriculum1.metrics['centrality'][1]}"
            )

    else:
        print(
            f"❌Curriculum 1 has a total centrality score of {curriculum1.metrics['centrality'][1]} and Curriculum2 has a total centrality score {curriculum2.metrics['centrality'][1]}"
        )
        metrics_same = False

    if curriculum1.metrics["max. centrality"] == curriculum2.metrics["max. centrality"]:
        if verbose:
            print(
                f"✅Curriculum 1 and Curriculum 2 have the same max centrality : {curriculum1.metrics['max. centrality']}"
            )

    else:
        print(
            f"❌Curriculum 1 has a max centrality of {curriculum1.metrics['max. centrality']} and Curriculum 2 has a max centrality of {curriculum2.metrics['max. centrality']}"
        )
        metrics_same = False

    # blocking factor and max blocking factor
    if (
        curriculum1.metrics["blocking factor"][1]
        == curriculum2.metrics["blocking factor"][1]
    ):
        if verbose:
            print(
                f"✅Curriculum 1 and Curriculum 2 have the same total blocking factor: {curriculum1.metrics['blocking factor'][1]}"
            )

    else:
        print(
            f"❌Curriculum 1 has a total blocking factor score of {curriculum1.metrics['blocking factor'][1]} and Curriculum2 has a total blocking factor score {curriculum2.metrics['blocking factor'][1]}"
        )
        metrics_same = False

    if (
        curriculum1.metrics["max. blocking factor"]
        == curriculum2.metrics["max. blocking factor"]
    ):
        if verbose:
            print(
                f"✅Curriculum 1 and Curriculum 2 have the same max blocking factor : {curriculum1.metrics['max. blocking factor']}"
            )

    else:
        print(
            f"❌Curriculum 1 has a max blocking factor of {curriculum1.metrics['max. blocking factor']} and Curriculum 2 has a max blocking factor of {curriculum2.metrics['max. blocking factor']}"
        )
        metrics_same = False

    # delay factor and max delay factor
    if curriculum1.metrics["delay factor"][1] == curriculum2.metrics["delay factor"][1]:
        if verbose:
            print(
                f"✅Curriculum 1 and Curriculum 2 have the same total delay factor: {curriculum1.metrics['delay factor'][1]}"
            )

    else:
        print(
            f"❌Curriculum 1 has a total delay factor score of {curriculum1.metrics['delay factor'][1]} and Curriculum2 has a total delay factor score {curriculum2.metrics['delay factor'][1]}"
        )
        metrics_same = False

    if (
        curriculum1.metrics["max. delay factor"]
        == curriculum2.metrics["max. delay factor"]
    ):
        if verbose:
            print(
                f"✅Curriculum 1 and Curriculum 2 have the same max delay factor : {curriculum1.metrics['max. delay factor']}"
            )

    else:
        print(
            f"❌Curriculum 1 has a max delay factor of {curriculum1.metrics['max. delay factor']} and Curriculum 2 has a max delay factor of {curriculum2.metrics['max. delay factor']}"
        )
        metrics_same = False

    # if the stats don't match up or we asked for a deep dive, take a deep dive!
    if not metrics_same or verbose:
        # print(f"Taking a look at courses")
        # make the initial changes array, i.e. what we're trying to explain
        explain = dict(
            {
                "complexity": curriculum2.metrics["complexity"][1]
                - curriculum1.metrics["complexity"][1],
                "centrality": curriculum2.metrics["centrality"][1]
                - curriculum1.metrics["centrality"][1],
                "blocking factor": curriculum2.metrics["blocking factor"][1]
                - curriculum1.metrics["blocking factor"][1],
                "delay factor": curriculum2.metrics["delay factor"][1]
                - curriculum1.metrics["delay factor"][1],
            }
        )

        runningTally = dict(
            {
                "complexity": 0.0,
                "centrality": 0.0,
                "blocking factor": 0.0,
                "delay factor": 0.0,
            }
        )

        all_results["to explain"] = explain
        all_results["matched courses"] = dict()
        all_results["unmatched courses"] = dict()
        # for each course in curriculum 1, try to find a similarly named course in curriculum 2
        for course in curriculum1.courses:
            # this is the catch: MATH 20A and MATH 20A or 10A are not going to match
            matching_course = filter(
                lambda x: x.name == course.name, curriculum2.courses
            )
            if len(matching_course) == 0:
                # if (redundants):
                #    # try one more time with the course_find method
                #    (found, course1_name, course2_name) = course_find(course.name, redundant_course_names, curriculum2)
                #    if (found)
                #        results = course_diff(course, course_from_name(course2_name, curriculum2), curriculum1, curriculum2, verbose)
                #        contribution = results["contribution to curriculum differences"]
                #        for (key, value) in runningTally
                #            runningTally[key] += contribution[key]

                #        all_results["matched courses"][course.name] = results
                #    else:
                # print(f"No matching course found for $(course.name)")
                # do stuff for courses with no match from c1 to c2
                # best idea here is to have a special diff for them
                # where everything is gained or lost
                #        results = course_diff_for_unmatched_course(course, curriculum1, true)
                #        contribution = results["contribution to curriculum differences"]
                #        for (key, value) in runningTally
                #            runningTally[key] += contribution[key]
                #
                #        all_results["unmatched courses"][course.name] = results

                # else:
                # print(f"No matching course found for $(course.name)")
                # do stuff for courses with no match from c1 to c2
                # best idea here is to have a special diff for them
                # where everything is gained or lost
                results = course_diff_for_unmatched_course(course, curriculum1, True)
                contribution = results["contribution to curriculum differences"]
                for key, value in runningTally:
                    runningTally[key] += contribution[key]

                all_results["unmatched courses"][course.name] = results

            elif len(matching_course) == 1:
                # print(f"Match found for $(course.name)")
                course2 = matching_course[1]
                results = course_diff(
                    course, course2, curriculum1, curriculum2, verbose
                )
                contribution = results["contribution to curriculum differences"]
                for key, value in runningTally:
                    runningTally[key] += contribution[key]
                all_results["matched courses"][course.name] = results
                # TODO: handle small bug in runningTally only containing the  results and no intermediate values
                # print(f"explained so far: $(runningTally["complexity"]), $(runningTally["centrality"]), $(runningTally["blocking factor"]), $(runningTally["delay factor"])")
            else:
                print(
                    f"Something weird here, we have more than one match for {course.name}"
                )
                # A choice... FOR NOW
                course2 = matching_course[1]
                results = course_diff(
                    course, course2, curriculum1, curriculum2, verbose
                )
                contribution = results["contribution to curriculum differences"]
                for key, value in runningTally:
                    runningTally[key] += contribution[key]

                all_results["matched courses"][course.name] = results

        for course in curriculum2.courses:
            matching_course = filter(
                lambda x: x.name == course.name, curriculum1.courses
            )
            if len(matching_course) == 0:
                # print(f"No matching course found for $(course.name)")
                # do stuff for courses with no match to c2 from c2
                # best idea here is to have a special diff for them
                # where everything is gained or lost
                results = course_diff_for_unmatched_course(course, curriculum2, False)
                contribution = results["contribution to curriculum differences"]
                for key, value in runningTally:
                    runningTally[key] += contribution[key]

                all_results["unmatched courses"][course.name] = results

        all_results["explained"] = dict(
            {
                "complexity": runningTally["complexity"],
                "centrality": runningTally["centrality"],
                "blocking factor": runningTally["blocking factor"],
                "delay factor": runningTally["delay factor"],
            }
        )

    # pretty_print_curriculum_results(all_results, desired_stat)
    # executive_summary_curriculum(all_results)
    return all_results
