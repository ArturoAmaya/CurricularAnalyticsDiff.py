import sys
from pathlib import Path
from typing import List

sys.path.append(str(Path(__file__).parent.parent.joinpath("src")))
import curricularanalytics as ca  # ignore the yellow squiggly line, PyLance is annoying if you don't use the conda distribution
from curricularanalytics import Curriculum, Course, Requisite
from curricularanalyticsdiff import HelperFns as hf
from curricularanalyticsdiff import Whatif as wi
from curricularanalyticsdiff import WhatifInstitutional as wii
import sys

print("What If Institutional")
condensed = ca.read_csv("./files/condensed2.csv")

affected = wii.add_course_institutional(
    "MATH 30",
    condensed,
    4.0,
    dict({"MATH 20A": Requisite.pre}),
    dict({"MATH 20B": Requisite.pre}),
)
print("done")
