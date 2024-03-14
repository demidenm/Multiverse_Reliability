[![Funded By](https://img.shields.io/badge/NIDA-F32%20DA055334--01A1-yellowgreen?style=plastic)](https://reporter.nih.gov/project-details/10525501)

[![RegReport](https://img.shields.io/badge/Stage_1-Registered_Report-red
)](https://doi.org/10.17605/OSF.IO/NQGEH)
[![Stage 2 RegReport DOI](https://img.shields.io/badge/DOI_Stage_2-Registered_Report_TBD-blue
)](https://doi.org)
[![AHRB Group Maps](https://img.shields.io/badge/AHRB_Group_Maps-NeuroVault-pink
)](https://identifiers.org/neurovault.collection:16605) 
[![AHRB Open Data](https://img.shields.io/badge/AHRB_Open_Data-OpenNeuro-pink
)](https://doi.org/10.18112/openneuro.ds005012.v1.0.1)
[![MLS Group Maps](https://img.shields.io/badge/MLS_Group_Maps-NeuroVault-orange
)](https://identifiers.org/neurovault.collection:16606)
[![MLS Open Data](https://img.shields.io/badge/MLS_Open_Data-OpenNeuro-orange
)](https://doi.org/10.18112/openneuro.ds005027.v1.0.1)
[![ABCD Group Maps](https://img.shields.io/badge/ABCD_Group_Maps-NeuroVault-black
)](https://identifiers.org/neurovault.collection:16777)


# Multiverse Reliability of the MID task
Project  Title: 

    Test-Retest Reliability in Functional Magnetic Resonance Imaging: Impact of Analytical Decisions on Individual and Group Estimates in the Monetary Incentive Delay Task_

Project Authors: 
    
    Michael I. Demidenko, Jeanette A. Mumford, Russell A. Poldrack

> Respository & code maintained by: Michael Demidenko
 
 
This github repository contains the Python (.py) and R scripts (.rmd/.html) that are associated with the project. \
This project is being submitted as a Registered Report. As described by the [OSF](https://doi.org/10.17605/OSF.IO/NQGEH), there are two stages to the \
registered report. Stage 1 is the submission and review of introduction, methods and proposed analyses for the publication.\
The Stage 2 is the completion of the analyses (as proposed), results and discussion section.



- Stage2_Code: Contains Python scripts, Jupyter notebooks, and cluster job files for stage 2 analysis.
  - brain_mask: Folder containing brain mask files.
  - cluster_jobs: Cluster job files for running analyses on Sherlock (AHRB/MLS) and MSI (ABCD).
  - compute_icc_permutations.py: Script for computing ICC permutations (240 models).
  - compute_icc_subsample.py: Script for computing ICC subsamples (Top ICC model).
  - extract_values.py: Script for extracting values (Used to calculate mFD, % probe acc, probe response times.
  - runs_withinrun_permutations.py: Script for within-run permutations, for each individual run 60 models * 4 contrasts.
  - runs_withinrun_single.py: Script for single within-run analysis, top ICC model for subsampling.
  - runs_withinsession_permutations.py: Script for within-session permutations, weighted fixed effect model for 60 models * 4 contrast.
  - run-analyses.ipynb: Jupyter notebook for running summary (maps avgs, distributions) on group and ICC output files for between-run estimates.
  - session-analyses.ipynb: Jupyter notebook for running summary (maps avgs, distributions) on group and ICC output files for between-session estimates.
  - taskreliabilty-run_descriptives.Rmd: R markdown file for descriptive task reliability analysis.
  - taskreliabilty-run_inferential.Rmd: R markdown file for inferential task reliability analysis.
  - taskreliabilty-session_descriptives.Rmd: R markdown file for descriptive session reliability analysis.
  - taskreliabilty-session_inferential.Rmd: R markdown file for inferential session reliability analysis.
  - upload_neurovault.py: Script for uploading group derivatives to NeuroVault.
  - output: folder contains the majority of estimates statistics used in the .Rmd analyses. Does not include ABCD data that includes subjects IDs (e.g. efficiencies, mFD, beh performance)

- Stage1_Code: Contains Python scripts and R markdown files from the Stage 1 Submission.
  - designmat_regressors_define.py: Script for defining design matrix regressors.
  - group_withinsession_permutations.py: Script for within-session group permutations.
  - runs_withinrun_permutations.py: Script for within-run permutations.
  - taskreliabilty_reporting.Rmd: R markdown file for reporting task reliability.
  - taskreliabilty_reporting.html: HTML output of the task reliability report.
