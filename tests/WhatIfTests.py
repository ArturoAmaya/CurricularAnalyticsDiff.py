import sys
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).parent.parent.joinpath("src")))
import curricularanalytics as ca  # ignore the yellow squiggly line, PyLance is annoying if you don't use the conda distribution
from curricularanalytics import Curriculum, Course, Requisite
from curricularanalyticsdiff import HelperFns as hf
from curricularanalyticsdiff import WhatIf as wi

print("What If Tests")
# test add course
curr = ca.read_csv("./files/SY-CurriculumPlan-BE25.csv")

new_course_name = "BENG 114"
new_course_credit_hours = 4.0  # defualt, you can change it to 1.0,2.0,3.0, etc
prereqs = dict(
    {"BENG 122A": Requisite.pre, "MATH 18": Requisite.pre, "MAE 140": Requisite.pre}
)
dependencies = dict(
    {"TE 2": Requisite.pre, "MAE 107": Requisite.pre, "CHEM 7L": Requisite.pre}
)

new_curric = wi.add_course(
    new_course_name, curr, new_course_credit_hours, prereqs, dependencies
)
assert new_curric.isvalid() == True
assert len(curr.courses) + 1 == len(new_curric.courses)
# test that the course has the right credit new_course_credit_hours
assert hf.course_from_name(new_course_name, new_curric).credit_hours == 4.0
assert hf.course_from_name(new_course_name, new_curric).name == "BENG 114"
assert hf.course_from_name(new_course_name, new_curric).requisites == dict(
    {
        hf.course_from_name("BENG 122A", new_curric).id: Requisite.pre,
        hf.course_from_name("MATH 18", new_curric).id: Requisite.pre,
        hf.course_from_name("MAE 140", new_curric).id: Requisite.pre,
    }
)
# check that the dependencies have it as a prereq
assert hf.course_from_name(new_course_name, new_curric) in hf.get_course_prereqs(
    hf.course_from_name("TE 2", new_curric), new_curric
)
assert hf.course_from_name(new_course_name, new_curric) in hf.get_course_prereqs(
    hf.course_from_name("MAE 107", new_curric), new_curric
)
assert hf.course_from_name(new_course_name, new_curric) in hf.get_course_prereqs(
    hf.course_from_name("CHEM 7L", new_curric), new_curric
)

# check that it's not in the old curriculum
assert hf.course_from_name(new_course_name, curr) is None

# Bad Input:
# bad course name shouldn't change anything
new_course_name_bad = "BENG 114A"
new_course_credit_hours_bad = 4.0  # defualt, you can change it to 1.0,2.0,3.0, etc
prereqs_bad = dict(
    {"BENG 122A": Requisite.pre, "MATH 18": Requisite.pre, "MAE 140": Requisite.pre}
)
dependencies_bad = dict(
    {"TE 2": Requisite.pre, "MAE 107": Requisite.pre, "CHEM 7L": Requisite.pre}
)
assert (
    wi.add_course(
        new_course_name_bad,
        curr,
        new_course_credit_hours_bad,
        prereqs_bad,
        dependencies_bad,
    ).isvalid()
    == True
)

# bad credit hours should also be fine
new_course_credit_hours_bad = 5.0
assert (
    wi.add_course(
        new_course_name_bad,
        curr,
        new_course_credit_hours_bad,
        prereqs_bad,
        dependencies_bad,
    ).isvalid()
    == True
)

# changing the name of a prereq should throw it way off
prereqs_bad = dict(
    {
        "BENG 122AA": Requisite.pre,  # DNE
        "MATH 18": Requisite.pre,
        "MAE 140": Requisite.pre,
    }
)
# this isn't the canonical best way to do this but it should work here
# https://discourse.julialang.org/t/how-to-test-a-default-error-raising-methods-message/19224/3
## assert_throws ArgumentError("I'm sorry, we couldn't find your requested prerequisite in the given curriculum. Are you sure its name matched the one in the file exactly?") add_course(new_course_name_bad, curr, new_course_credit_hours_bad, prereqs_bad, dependencies_bad)

# changing the name of a dependency should also throw it off
prereqs_bad = dict(
    {
        "BENG 122A": Requisite.pre,  # DNE
        "MATH 18": Requisite.pre,
        "MAE 140": Requisite.pre,
    }
)
dependencies_bad = dict(
    {"TE 22": Requisite.pre, "MAE 107": Requisite.pre, "CHEM 7L": Requisite.pre}  # DNE
)
##assert_throws ArgumentError("I'm sorry, we couldn't find your requested dependent course in the given curriculum. Are you sure its name matched the one in the file exactly?") add_course(new_course_name_bad, curr, new_course_credit_hours_bad, prereqs_bad, dependencies_bad)

# =
# -------------------------------------------------------
# Remove a course
# -------------------------------------------------------
# =#
curr = ca.read_csv("./files/SY-CurriculumPlan-BE25.csv")

course_to_remove = "MATH 20D"

new_curric = wi.remove_course(course_to_remove, curr)
assert new_curric.isvalid() == True
assert not ("MATH 20D" in hf.courses_to_course_names(new_curric.courses))
assert "MATH 20D" in hf.courses_to_course_names(curr.courses)
assert (
    len(hf.course_from_name("BENG 130", curr).requisites)
    == len(hf.course_from_name("BENG 130", new_curric).requisites) + 1
)
assert (
    len(hf.courses_that_depend_on_me(hf.course_from_name("MATH 20C", curr), curr))
    == len(
        hf.courses_that_depend_on_me(
            hf.course_from_name("MATH 20C", new_curric), new_curric
        )
    )
    + 1
)

# bad input
# Just a bad name
course_to_remove = "MATH 20DD"
##assert_throws ArgumentError("I'm sorry, we couldn't find your requested course in the given curriculum. Are you sure its name matched the one in the file exactly?") remove_course(course_to_remove, curr)
# =
# -------------------------------------------------------
# Add a Prerequisite
# -------------------------------------------------------
# =#
curr = ca.read_csv("./files/SY-CurriculumPlan-BE25.csv")

course_name = "BENG 140B"
prerequisite = "BENG 125"
req_type = Requisite.pre

new_curric = wi.add_prereq(course_name, prerequisite, curr, req_type)
assert new_curric.isvalid() == True

# test it's hooked up right
assert (
    len(hf.courses_that_depend_on_me(hf.course_from_name("BENG 125", curr), curr))
    == len(
        hf.courses_that_depend_on_me(
            hf.course_from_name("BENG 125", new_curric), new_curric
        )
    )
    - 1
)
assert (
    hf.course_from_name("BENG 140B", new_curric).requisites[
        hf.course_from_name("BENG 125", new_curric).id
    ]
    == Requisite.pre
)

# TODO
# bad course name will throw it off
course_name = "BENG 140BB"
##assert_throws ArgumentError("I'm sorry, we couldn't find your requested course in the given curriculum. Are you sure its name matched the one in the file exactly?") add_prereq(course_name, prerequisite, curr, req_type)

course_name = "BENG 140B"
# bad prerequisite throws it off
prerequisite = "BENG 1255"
##assert_throws ArgumentError("I'm sorry, we couldn't find your requested prerequisite in the given curriculum. Are you sure its name matched the one in the file exactly?") add_prereq(course_name, prerequisite, curr, req_type)

# =
# -------------------------------------------------------
# Remove a Prerequisite
# -------------------------------------------------------
# =#
curr = ca.read_csv("./files/SY-CurriculumPlan-BE25.csv")

course_name = "BENG 100"
prerequisite = "MATH 20C"

new_curric = wi.remove_prereq(course_name, prerequisite, curr)
assert new_curric.isvalid() == True

assert (
    len(hf.course_from_name("BENG 100", curr).requisites)
    == len(hf.course_from_name("BENG 100", new_curric).requisites) + 1
)
assert (
    len(hf.courses_that_depend_on_me(hf.course_from_name("MATH 20C", curr), curr))
    == len(
        hf.courses_that_depend_on_me(
            hf.course_from_name("MATH 20C", new_curric), new_curric
        )
    )
    + 1
)
assert hf.course_from_name("BENG 100", new_curric).requisites == dict(
    {
        hf.course_from_name("BENG 1", new_curric).id: Requisite.pre,
        hf.course_from_name("MATH 18", new_curric).id: Requisite.pre,
    }
)

# bad input
# bad course name will throw it off
course_name = "beng 1000"
##assert_throws ArgumentError("I'm sorry, we couldn't find your requested course in the given curriculum. Are you sure its name matched the one in the file exactly?") remove_prereq(course_name, prerequisite, curr)

# bad prereq name will throw it off
course_name = "BENG 100"
prerequisite = "MATH 2C"
##assert_throws ArgumentError("I'm sorry, we couldn't find your requested prerequisite in the given curriculum. Are you sure its name matched the one in the file exactly?") remove_prereq(course_name, prerequisite, curr)
