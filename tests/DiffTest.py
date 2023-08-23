import sys
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).parent.parent.joinpath("src")))
import curricularanalytics as ca  # ignore the yellow squiggly line, PyLance is annoying if you don't use the conda distribution
from curricularanalytics import Curriculum, Course
from curricularanalyticsdiff import HelperFns as hf
from curricularanalyticsdiff import Diff as diff
import json

print("Diff tests")
test = ca.read_csv("./files/SY-CurriculumPlan-BE25.csv")


# curricular diff
## same curriculum.
### No params Requires some visual check that all the printed lines are using the checkmark emoji
f = open("./tests/test_w_itself.json")
assert diff.curricular_diff(test, test) == f
f.close()
## same curriculum
### verbose off. Shouldn't ever detect there's a difference and should just return empty values
assert diff.curricular_diff(test, test, False) == dict()

## same curriculum
### redundants... TODO

## different years of the same curriculum - CE25 2015 and 2016
test1 = ca.read_csv("./files/SY-CurriculumPlan-CE252015.csv")
test2 = ca.read_csv("./files/SY-CurriculumPlan-CE252016.csv")

### no params
f = open("./tests/ce252015_toce252016.json")
assert diff.curricular_diff(test1, test2) == f
f.close()
#### verbose off. should return the same as verbose on since there are noticeable differences
f = open("./tests/testce2515toce2516false.json")
assert diff.curricular_diff(test1, test2, False) == f
f.close()

### redundants too because that is a lot of work

# course diff
## same course, same curriculum
assert diff.course_diff(
    test1.courses[3], test1.courses[3], test1, test1, False
) == dict(
    {
        "complexity": dict({"course 1 score": 12.7, "course 2 score": 12.7}),
        "c1 name": "Chemical Engineering",
        "centrality": dict({"course 1 score": 0, "course 2 score": 0}),
        "contribution to curriculum differences": dict(
            {
                "complexity": 0.0,
                "centrality": 0.0,
                "blocking factor": 0.0,
                "delay factor": 0.0,
            }
        ),
        "prereqs": dict({"gained prereqs": List[str], "lost prereqs": List[str]}),
        "blocking factor": dict({"course 1 score": 12, "course 2 score": 12}),
        "c2 name": "Chemical Engineering",
        "delay factor": dict({"course 1 score": 7.0, "course 2 score": 7.0}),
    }
)
# TODO rest
