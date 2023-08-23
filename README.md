### CurricularAnalyticsDiff.py
Python package to run the same functions of CurricularAnalyticsDiff.jl

NOTE: this particular version uses large course id values. I experienced integer overflow, so I changed lines 110 and 124 in CSVUtilities.py in curricularanalytics to use `c_ID: int = int(row["Course ID"]) if int(row["Course ID"]) > 0 else 2**32 + int(row["Course ID"])`
There are also two edits in the package functionality, so use [this fork for now](https://github.com/ArturoAmaya/CurricularAnalytics.py). See the commit messages for explanations