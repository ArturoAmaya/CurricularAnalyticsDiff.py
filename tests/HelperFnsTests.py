import sys
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).parent.parent.joinpath("src")))
import curricularanalytics as ca  # ignore the yellow squiggly line, PyLance is annoying if you don't use the conda distribution
from curricularanalytics import Curriculum, Course
from curricularanalyticsdiff import HelperFns as hf

print("starting test")

test = ca.read_csv("./files/SY-CurriculumPlan-BE25.csv")

# prereq_print
assert type(hf.prereq_print((["MATH 20A", "MATH 20B", "MATH 20E"]))) == str
assert (
    hf.prereq_print((["MATH 20A", "MATH 20B", "BENG 110", "CALC 87"]))
    == " " + " ".join(["MATH 20A", "MATH 20B", "BENG 110", "CALC 87"]) + " "
)
assert hf.prereq_print([""]) == "  "
assert hf.prereq_print([]) == " "


# course from name
assert hf.course_from_name("MATH 20A", test) is test.courses[2 - 1]
assert hf.course_from_name("PHYS 2A", test) is test.courses[5 - 1]
assert type(hf.course_from_name("BENG 130", test)) == Course
# test for 0.1.5 course name update
test2 = ca.read_csv("./files/massive/output2022/MA30/FI.csv")
# these courses are called MATH 20D/MATH 109 and MATH 109/MATH 20D but one has prefix + name MATH 20D and the other has prefix + name MATH 109
assert (
    hf.course_from_name("MATH 20D", test2.curriculum) is test2.curriculum.courses[8 - 1]
)
assert (
    hf.course_from_name("MATH 109", test2.curriculum)
    is test2.curriculum.courses[10 - 1]
)

# get course prereqs
assert hf.get_course_prereqs(test.courses[2 - 1], test) == []  # Vector{Course}()
assert hf.get_course_prereqs(test.courses[5 - 1], test) == [
    test.courses[2 - 1]
]  # Vector{Course}([test.courses[2]])
assert type(hf.get_course_prereqs(test.courses[5 - 1], test)) == list
assert hf.get_course_prereqs(test.courses[22 - 1], test) == [
    test.courses[6 - 1],
    test.courses[15 - 1],
    test.courses[7 - 1],
]
assert set(hf.get_course_prereqs(test.courses[26 - 1], test)) == set(
    [
        test.courses[5 - 1],
        test.courses[4 - 1],
        test.courses[2 - 1],
        test.courses[11 - 1],
        test.courses[8 - 1],
        test.courses[14 - 1],
        test.courses[3 - 1],
    ]
)  # INFO: THEY ARE NOT IN THAT ORDER, WHICH IS WHY BOTH STATEMENTS ARE WRAPPED IN SETS
assert hf.get_course_prereqs(test.courses[26 - 1], test) == [
    test.courses[3 - 1],
    test.courses[2 - 1],
    test.courses[4 - 1],
    test.courses[5 - 1],
    test.courses[8 - 1],
    test.courses[11 - 1],
    test.courses[14 - 1],
]  # 3;2;4;5;8;11;14 is the order stated in the file itself *shrug*
assert hf.get_course_prereqs(test.courses[26 - 1], test) != [
    test.courses[4 - 1],
    test.courses[5 - 1],
    test.courses[11 - 1],
    test.courses[8 - 1],
    test.courses[14 - 1],
    test.courses[2 - 1],
    test.courses[3 - 1],
]
assert set(hf.get_course_prereqs(test.courses[26 - 1], test)) == set(
    [
        test.courses[4 - 1],
        test.courses[5 - 1],
        test.courses[11 - 1],
        test.courses[8 - 1],
        test.courses[14 - 1],
        test.courses[2 - 1],
        test.courses[3 - 1],
    ]
)

# courses that depend on me (first level only)
assert type(hf.courses_that_depend_on_me(test.courses[10 - 1], test)) == list
assert hf.courses_that_depend_on_me(test.courses[1 - 1], test) == [
    test.courses[3 - 1],
    test.courses[16 - 1],
]
assert hf.courses_that_depend_on_me(test.courses[8 - 1], test) == [
    test.courses[13 - 1],
    test.courses[16 - 1],
    test.courses[26 - 1],
]
assert hf.courses_that_depend_on_me(test.courses[8 - 1], test) != [
    test.courses[16 - 1],
    test.courses[13 - 1],
    test.courses[26 - 1],
]

# longest path to me
assert (
    type(hf.longest_path_to_me(test.courses[11 - 1], test, test.courses[11 - 1], False))
    == list
)
assert hf.longest_path_to_me(
    test.courses[11 - 1], test, test.courses[11 - 1], False
) == [
    test.courses[2 - 1],
    test.courses[4 - 1],
    test.courses[7 - 1],
    test.courses[11 - 1],
]
assert hf.longest_path_to_me(
    hf.course_from_name("BENG 110", test), test, test.courses[24 - 1], False
) == [
    hf.course_from_name("MATH 20A", test),
    hf.course_from_name("MATH 20B", test),
    hf.course_from_name("MATH 20C", test),
    hf.course_from_name("PHYS 2C", test),
    hf.course_from_name("BENG 110", test),
]  # canonical longest path to BENG 110 is 20a, 20b, 20c, 20d, but python pkg returns the equally valid 20a,20b, 20c, phys 2c TODO: look into IDing other longest paths
# canonical longest path through to phys 2b is math 20a phys 2a phys2b
assert hf.longest_path_to_me(
    hf.course_from_name("PHYS 2B", test), test, test.courses[8 - 1], False
) == [test.courses[2 - 1], test.courses[5 - 1], test.courses[8 - 1]]
# alt longest path through to phys2b is math20a, math20b, phys 2b. This should return math20b, phys 2b
assert hf.longest_path_to_me(
    hf.course_from_name("PHYS 2B", test), test, test.courses[4 - 1], True
) == [test.courses[4 - 1], test.courses[8 - 1]]
assert hf.longest_path_to_me(
    hf.course_from_name("PHYS 2B", test), test, test.courses[9 - 1], True
) == [hf.course_from_name("PHYS 2B", test)]

# course to course names
assert (
    type(
        hf.courses_to_course_names(
            [
                test.courses[11 - 1],
                test.courses[12 - 1],
                test.courses[15 - 1],
                test.courses[18 - 1],
            ]
        )
    )
    == list
)  # Vector{AbstractString}
assert hf.courses_to_course_names(
    [
        test.courses[11 - 1],
        test.courses[12 - 1],
        test.courses[15 - 1],
        test.courses[18 - 1],
    ]
) == ["MATH 20D", "CHEM 7L", "MATH 18", "MAE 8"]

# blocking factor investigator
assert set(hf.blocking_factor_investigator(test.courses[8 - 1], test)) == set(
    [
        test.courses[13 - 1],
        test.courses[26 - 1],
        test.courses[16 - 1],
        test.courses[20 - 1],
        test.courses[28 - 1],
        test.courses[29 - 1],
        test.courses[25 - 1],
    ]
)
assert hf.blocking_factor_investigator(test.courses[8 - 1], test) == [
    test.courses[13 - 1],
    test.courses[16 - 1],
    test.courses[26 - 1],
    test.courses[25 - 1],
    test.courses[20 - 1],
    test.courses[28 - 1],
    test.courses[29 - 1],
]
assert set(hf.blocking_factor_investigator(test.courses[11 - 1], test)) == set(
    [
        test.courses[24 - 1],
        test.courses[26 - 1],
        test.courses[27 - 1],
        test.courses[31 - 1],
        test.courses[30 - 1],
        test.courses[34 - 1],
        test.courses[38 - 1],
        test.courses[32 - 1],
        test.courses[33 - 1],
        test.courses[36 - 1],
        test.courses[37 - 1],
    ]
)
assert hf.blocking_factor_investigator(test.courses[11 - 1], test) == [
    test.courses[24 - 1],
    test.courses[26 - 1],
    test.courses[27 - 1],
    test.courses[34 - 1],
    test.courses[30 - 1],
    test.courses[31 - 1],
    test.courses[32 - 1],
    test.courses[38 - 1],
    test.courses[33 - 1],
    test.courses[36 - 1],
    test.courses[37 - 1],
]
assert hf.blocking_factor_investigator(test.courses[43 - 1], test) == []

# delay factor investigator
# Note that this doesn't match the canonical longest path determined in the visualization software. This is interesting.
assert hf.delay_factor_investigator(test.courses[8 - 1], test) == [
    test.courses[2 - 1],
    test.courses[5 - 1],
    test.courses[8 - 1],
    test.courses[13 - 1],
    test.courses[25 - 1],
    test.courses[28 - 1],
]
assert type(hf.delay_factor_investigator(test.courses[8 - 1], test)) == list
assert hf.delay_factor_investigator(test.courses[43 - 1], test) == [
    test.courses[43 - 1]
]

# centrality investigator
## the centrlaity investigator doesn't track centrality paths for sink or source nodes. It should though. that's an issue for later TODO
assert hf.centrality_investigator(test.courses[1 - 1], test) == []
assert hf.centrality_investigator(test.courses[37 - 1], test) == []
# a simple one path test
assert hf.centrality_investigator(test.courses[35 - 1], test) == [
    [
        hf.course_from_name("MAE 140", test),
        hf.course_from_name("BENG 122A", test),
        hf.course_from_name("BENG 125", test),
    ]
]
# a multiple path test
result = hf.centrality_investigator(hf.course_from_name("PHYS 2B", test), test)
canonical_result = [
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("MATH 20B", test),
        hf.course_from_name("PHYS 2B", test),
        hf.course_from_name("PHYS 2CL", test),
        hf.course_from_name("MAE 170", test),
        hf.course_from_name("BENG 186B", test),
    ],
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("MATH 20B", test),
        hf.course_from_name("PHYS 2B", test),
        hf.course_from_name("PHYS 2CL", test),
        hf.course_from_name("MAE 170", test),
        hf.course_from_name("BENG 172", test),
    ],
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("MATH 20B", test),
        hf.course_from_name("PHYS 2B", test),
        hf.course_from_name("BENG 130", test),
    ],
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("MATH 20B", test),
        hf.course_from_name("PHYS 2B", test),
        hf.course_from_name("BENG 140A", test),
        hf.course_from_name("BENG 140B", test),
    ],
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("PHYS 2A", test),
        hf.course_from_name("PHYS 2B", test),
        hf.course_from_name("PHYS 2CL", test),
        hf.course_from_name("MAE 170", test),
        hf.course_from_name("BENG 186B", test),
    ],
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("PHYS 2A", test),
        hf.course_from_name("PHYS 2B", test),
        hf.course_from_name("PHYS 2CL", test),
        hf.course_from_name("MAE 170", test),
        hf.course_from_name("BENG 172", test),
    ],
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("PHYS 2A", test),
        hf.course_from_name("PHYS 2B", test),
        hf.course_from_name("BENG 130", test),
    ],
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("PHYS 2A", test),
        hf.course_from_name("PHYS 2B", test),
        hf.course_from_name("BENG 140A", test),
        hf.course_from_name("BENG 140B", test),
    ],
]
assert set(tuple(i) for i in result) == set(tuple(i) for i in canonical_result)

# a second multiple path test
result = hf.centrality_investigator(hf.course_from_name("MATH 20D", test), test)
canonical_result = [
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("MATH 20B", test),
        hf.course_from_name("MATH 20C", test),
        hf.course_from_name("MATH 20D", test),
        hf.course_from_name("BENG 130", test),
    ],
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("MATH 20B", test),
        hf.course_from_name("MATH 20C", test),
        hf.course_from_name("MATH 20D", test),
        hf.course_from_name("BENG 110", test),
        hf.course_from_name("BENG 112A", test),
        hf.course_from_name("BENG 103B", test),
    ],
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("MATH 20B", test),
        hf.course_from_name("MATH 20C", test),
        hf.course_from_name("MATH 20D", test),
        hf.course_from_name("BENG 110", test),
        hf.course_from_name("BENG 112A", test),
        hf.course_from_name("BENG 112B", test),
        hf.course_from_name("BENG 186A", test),
    ],
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("MATH 20B", test),
        hf.course_from_name("MATH 20C", test),
        hf.course_from_name("MATH 20D", test),
        hf.course_from_name("BENG 110", test),
        hf.course_from_name("BENG 112A", test),
        hf.course_from_name("BENG 187A", test),
        hf.course_from_name("BENG 187B", test),
        hf.course_from_name("BENG 187C", test),
        hf.course_from_name("BENG 187D", test),
    ],
    [
        hf.course_from_name("MATH 20A", test),
        hf.course_from_name("MATH 20B", test),
        hf.course_from_name("MATH 20C", test),
        hf.course_from_name("MATH 20D", test),
        hf.course_from_name("BENG 110", test),
        hf.course_from_name("MAE 150", test),
    ],
]
assert set(tuple(i) for i in result) == set(tuple(i) for i in canonical_result)

print("all tests passed")
