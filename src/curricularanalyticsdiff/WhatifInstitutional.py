import curricularanalytics as ca
from typing import List
from curricularanalytics import Course, Curriculum, Requisite
import curricularanalyticsdiff.HelperFns as hf
from curricularanalyticsdiff.Whatif import (
    add_course,
    remove_course,
    add_prereq,
    remove_prereq,
)
import copy

"""
    print_affected_plans(affected_plans:Vector{String})
Print a list of the plans affected by a change and return how many plans were affected.
"""


# TODO fix this, it's printing weird in Python
def print_affected_plans(affected_plans):
    prev_major = "PL99"
    count = 0
    for major in affected_plans:
        if major != "":
            if major[0:3] != prev_major[0:3]:
                prev_major = major
                print(f"\n{major[0:4]}: {major[4:]}, ")
                count += 1
            elif (
                major != prev_major
            ):  # don't ask me why for some reason each plan code shows up multiple times
                prev_major = major
                print(f"{major[4:]}, ")
                count += 1
    print()
    return count


"""
    delete_prerequisite_institutional(target:str, prereq:str, curriculum:Curriculum)
Remove the course with name `prereq` from being a prerequisite to the course with name `target` in `curriculum` and print how many degree plans were affected.
"""


def delete_prerequisite_institutional(target: str, prereq: str, curriculum: Curriculum):
    target_course = hf.course_from_name(target, curriculum)
    # error check
    if target_course is None:
        raise ValueError(
            "I'm sorry, we couldn't find your target course in the given curriculum. Make sure you got the name exactly right."
        )

    prereq_course = hf.course_from_name(prereq, curriculum)
    # error check
    if prereq_course is None:
        raise ValueError(
            "I'm sorry, we couldn't find your prerequisite course in the given curriculum. Make sure you got the name exactly right."
        )

    # deepcopy to leave the curriculum unaltered
    target_course = copy.deepcopy(target_course)
    prereq_course = copy.deepcopy(prereq_course)

    # delete_requisite!(prereq_course, target_course)
    target_course.delete_requisite(prereq_course)

    target_course_majors = target_course.canonical_name.split(",")
    prereq_course_majors = prereq_course.canonical_name.split(",")
    print()
    ret = set(target_course_majors).intersection(
        set(prereq_course_majors)
    )  # intersect(set(target_course_majors), set(prereq_course_majors))
    ret = sorted(ret)
    if ret[0] == "":
        ret.pop(0)  # popfirst!(ret)

    count = print_affected_plans(ret)
    print(f"Number of affected plans: {count}")
    return ret


# def  delete_prerequisite_institutional!(target:str, prereq:str, curriculum:Curriculum)
#     target_course =hf.course_from_name(target, curriculum)
#     # error check
#     if typeof(target_course) == Nothing
#         raise ValueError("I'm sorry, we couldn't find your target course in the given curriculum. Make sure you got the name exactly right."))

#     prereq_course =hf.course_from_name(prereq, curriculum)
#     # error check
#     if typeof(prereq_course) == Nothing
#         raise ValueError("I'm sorry, we couldn't find your prerequisite course in the given curriculum. Make sure you got the name exactly right."))


#     # no deepcopy here
#     delete_requisite!(prereq_course, target_course)

#     target_course_majors = split(target_course.canonical_name, ",")
#     prereq_course_majors = split(prereq_course.canonical_name, ",")
#     print()
#     ret = intersect(set(target_course_majors), set(prereq_course_majors))
#     ret = sort(collect(ret))
#     if ret[1] == ""
#         popfirst!(ret)

#     count = print_affected_plans(ret)
#     print("Number of affected plans: $(count)")
#     return ret


"""
    delete_course_institutional(course_to_remove_name:str, curriculum:Curriculum)
Remove the course with name `course_to_remove_name` from `curriculum` and print how many degree plans were affected.
"""


def delete_course_institutional(course_to_remove_name: str, curriculum: Curriculum):
    course_to_remove = hf.course_from_name(course_to_remove_name, curriculum)
    if course_to_remove is None:
        raise ValueError(
            "I'm sorry, we couldn't find your target course in the given curriculum. Make sure you got the name exactly right."
        )

    centrality_paths = hf.centrality_investigator(course_to_remove, curriculum)
    if len(centrality_paths) > 0:
        prereq_set = set()
        dep_set = set()
        for path in centrality_paths:
            my_index = [i for i, x in enumerate(path) if x == course_to_remove][
                0
            ]  # findall(x -> x == course_to_remove, path)[1]
            my_prereqs = path[0 : my_index - 1]
            my_deps = path[my_index + 1 : -1]
            path_set = set()
            for dep in my_deps:
                if len(path_set) == 0:
                    path_set = set(dep.canonical_name.split(","))
                else:
                    path_set = path_set.union(set(dep.canonical_name.split(",")))

            dep_set = dep_set.union(path_set)

        full_set = prereq_set.union(dep_set)
        # don't forget all the instances where the removed course is the end of a chain and has no prereqs
        # this was what we used to take a look at: just the course's majors. now use the dependents to
        # so that courses listed under a different name also get factored in here. MATH 20C vs MATH 20C/31BH
        full_set = full_set.union(set(course_to_remove.canonical_name.split(",")))
        full_set = sorted(full_set)
        count = print_affected_plans(full_set)
        print(f"Number of affected plans: {count}")
        return full_set
    else:
        # print("This course hasn't been hooked up to anything. It doesn't affect any plans other than the one it is in")
        full_set = sorted(set(course_to_remove.canonical_name.split(",")))
        count = print_affected_plans(full_set)
        print(f"Number of affected plans: {count}")
        return full_set


# def  delete_course_institutional!(course_to_remove_name:str, curriculum:Curriculum)
#     course_to_remove =hf.course_from_name(course_to_remove_name, curriculum)
#     if typeof(course_to_remove) == Nothing
#         raise ValueError("I'm sorry, we couldn't find your target course in the given curriculum. Make sure you got the name exactly right."))

#     affected_majors = split(course_to_remove.canonical_name, ",")
#     count = print_affected_plans(affected_majors)
#     print("Number of affected plans: $(count)")

#     # let's change the curriculum
#     # note: this works on a technicality, pending ! versions of the core what if def s
#     curriculum = remove_course(curriculum, course_to_remove_name)
#     print(length(curriculum.courses))
#     return (affected_majors, curriculum)


"""
    add_course_institutional(new_course_name:str, curriculum:Curriculum, new_course_credit_hours:float, prereqs:Dict, dependencies:Dict)
Add a course with name `new_course_name` and provided characteristics to `curriculum`` and print how many degree plans are affected.
"""


def add_course_institutional(
    new_course_name: str,
    curriculum: Curriculum,
    new_course_credit_hours: float,
    prereqs: dict,
    dependencies: dict,
):
    new_curriculum = add_course(
        new_course_name, curriculum, new_course_credit_hours, prereqs, dependencies
    )
    # TODO error checking on this one
    # errors = IOBuffer()
    new_curriculum.isvalid()
    # get all the paths that depend on me
    ## first, get me
    # UCSD = read_csv("./targets/condensed.csv");
    course = hf.course_from_name(new_course_name, new_curriculum)
    my_centrality_paths = hf.centrality_investigator(course, new_curriculum)
    # for debugging my_centrality_paths = sorted(my_centrality_paths, key=lambda x: x[0].name)
    if len(my_centrality_paths) > 0:
        # ok actually do stuff
        # the gist is:
        # look at all the paths that I'm a prereq for and for each path take the intersection of their majors
        ## get all the paths that depend on me:
        prereq_set = set()
        dep_set = set()
        for path in my_centrality_paths:
            my_index = [i for i, x in enumerate(path) if x == course][
                0
            ]  # findall(x -> x == course, path)[1]
            # course is path[my_index]
            # TODO: edge cases based on length
            my_prereqs = path[0 : my_index - 1]
            my_deps = path[my_index + 1 :]
            # #= HUGE EDIT: only analyze the dependencies
            # path_set = set()
            # for prereq in my_prereqs:
            #     if len(path_set) == 0:
            #         path_set = set(prereq.canonical_name.split(","))
            #     else:
            #         path_set.intersect(set(prereq.canonical_name.split(",")))

            # prereq_set.union(path_set)
            # =#
            path_set = set()
            for dep in my_deps:
                if len(path_set) == 0:
                    path_set = set(dep.canonical_name.split(","))
                else:
                    path_set = path_set.union(set(dep.canonical_name.split(",")))

            dep_set = dep_set.union(path_set)

        full_set = prereq_set.union(dep_set)
        full_set = sorted(full_set)
        count = print_affected_plans(full_set)
        print(f"Number of affected plans: {count}")
        # look at all the paths that depend on me and for each path take the union of their majors
        # then combine the two sets
        return full_set
        # if we're adding riiiight at the beginning of the sequence it is a sink (centrality 0) but definitely affects a lot of majors
    elif len(my_centrality_paths) == 0:
        full_set = set()
        for dep in hf.courses_that_depend_on_me(course, new_curriculum):
            full_set = full_set.union(set(dep.canonical_name.split(",")))

        full_set = sorted(full_set)
        print(full_set)
        print("Added to the beginning, or not hooked up to anything important")
        return full_set
    else:
        # ok this seems to not affect any majors because it's not been hooked up to anything
        print(
            "This course hasn't been hooked up to anything, it didn't affect any majors other than the one it is in"
        )
        full_set = set()
        return full_set


# # TODO: edit to add the
# def  add_course_institutional!(course_name:str, curriculum:Curriculum, new_course_credit_hours:float, prereqs:Dict, dependencies:Dict)
#     new_curriculum = add_course(curriculum, course_name, new_course_credit_hours, prereqs, dependencies)
#     # TODO error checking on this one
#     errors = IOBuffer()
#     isvalid_curriculum(new_curriculum, errors)
#     # get all the paths that depend on me
#     ## first, get me
#     #UCSD = read_csv("./targets/condensed.csv");
#     course =hf.course_from_name(new_course_name, new_curriculum)
#     my_centrality_paths = centrality_investigator(course, new_curriculum)
#     if length(my_centrality_paths) > 0
#         # ok actually do stuff
#         # the gist is:
#         # look at all the paths that I'm a prereq for and for each path take the intersection of their majors
#         ## get all the paths that depend on me:
#         prereq_set = set()
#         dep_set = set()
#         for path in my_centrality_paths
#             my_index = findall(x -> x == course, path)[1]
#             # course is path[my_index]
#             # TODO: edge cases based on length
#             my_prereqs = path[1:my_index-1]
#             my_deps = path[my_index+1:end]
#             #= HUGE EDIT: only analyze the dependencies
#             path_set = set()
#             for prereq in my_prereqs
#                 if isempty(path_set)
#                     path_set = set(split(prereq.canonical_name,","))
#                 else
#                     intersect!(path_set,set(split(prereq.canonical_name,",")))


#             union!(prereq_set,path_set)
#             =#
#             path_set = set()
#             for dep in my_deps
#                 if isempty(path_set)
#                     path_set = set(split(dep.canonical_name, ","))
#                 else
#                     union!(path_set, set(split(dep.canonical_name, ",")))


#             union!(dep_set, path_set)


#         full_set = union(prereq_set, dep_set)
#         full_set = sort(collect(full_set))
#         count = print_affected_plans(full_set)
#         print("Number of affected plans: $(count)")
#         # look at all the paths that depend on me and for each path take the union of their majors
#         # then combine the two sets
#         return full_set, new_curriculum
#     else
#         # ok this seems to not affect any majors because it's not been hooked up to anything
#         print("This course hasn't been hooked up to anything, it didn't affect any majors other than the one it is in")
#         full_set = set()
#         return full_set, new_curriculum


"""
    add_prereq_institutional(curriculum:Curriculum, course_with_new_prereq:str, prereq:str)
Print how many plans are affected by adding a prerequisite to `course_with_new_prereq` in `curriculum`.

Note that it currently does not actually add `prereq` as a prerequisite to `course_with_new_prereq`
"""


def add_prereq_institutional(
    curriculum: Curriculum, course_with_new_prereq: str, prereq: str
):
    # TODO: actually add in the prereq
    course_with_new_prereq = hf.course_from_name(course_with_new_prereq, curriculum)
    if course_with_new_prereq is None:
        raise ValueError(
            "I'm sorry, we couldn't find your target course in the given curriculum. Make sure you got the name exactly right."
        )

    affected_majors = course_with_new_prereq.canonical_name.split(",")

    count = print_affected_plans(affected_majors)
    print(f"Number of affected plans: {count}")
    # NOTE THIS DOESNT ACTUALLY CHANGE THE CURRICULUM OBJECT OK?
    # also note that this doesn't explain HOW the affected plans are affected, simply that they are
    return affected_majors


# def  add_prereq_institutional!(curriculum:Curriculum, course_with_new_prereq:str, prereq:str)
#     course_with_new_prereq_course =hf.course_from_name(course_with_new_prereq, curriculum)
#     if typeof(course_with_new_prereq) == Nothing
#         raise ValueError("I'm sorry, we couldn't find your target course in the given curriculum. Make sure you got the name exactly right."))

#     new_curric = add_prereq(curriculum, course_with_new_prereq, prereq, pre)
#     affected_majors = split(course_with_new_prereq_course.canonical_name, ",")

#     count = print_affected_plans(affected_majors)
#     print("Number of affected plans: $(count)")
#     # NOTE THIS DOESNT ACTUALLY CHANGE THE CURRICULUM OBJECT OK?
#     # also note that this doesn't explain HOW the affected plans are affected, simply that they are
#     return affected_majors, new_curric


## what is in the 20c canon name but not in the calculated set
# sort(collect(setdiff(set(split(course.canonical_name,",")),affected)))
