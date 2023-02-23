---
title: 'Spreadsheet Energy System Model Generator (SESMG): A tool for the optimization of urban energy systems'
tags:
  - Python
  - Energy System Modeling
  - Urban Energy System
  - Optimization
  - Multi-Energy Systems
authors:
  - name: Christian Klemm
    corresponding: true # (This is how to denote the corresponding author)
    orcid: 0000-0003-0801-4178
    affiliation: "1, 2"
  - name: Gregor Becker
    orcid: 0000-0001-8803-6873
    affiliation: 1
  - name: Janik Budde
    orcid: 0000-0002-1617-5900
    affiliation: 1
  - name: Jan Tockloth
    orcid: 0000-0003-2582-1043
    affiliation: 1
  - name: Peter Vennemann
    orcid: 0000-0002-0767-5014
    affiliation: 1
affiliations:
 - name: Department of Energy, Building Services and Environmental Engineering, Münster University of Applied Sciences, Germany
   index: 1
 - name: Department of Energy and Environmental Management, Europa-Universität Flensburg, Germany 
   index: 2
date: 31 March 2023
bibliography: paper.bib

---
# Summary

...

# Statement of need
Due to volatile renewable energy sources, the use of different energy storage systems, sector coupling, the growing importance of new sectors such as e-mobility and hydrogen usage, as well as the increasing relevance of multiple planning objectives, it is becoming increasingly difficult to optimally design urban energy systems [@Zhang.2018]. In this context, urban energy systems are defined as “the combined process of acquiring and using energy in a given spatial entity with a high density and differentiation of residents, buildings, commercial sectors, infrastructure, and energy sectors (e.g., heat, electricity, fuels). They are also called mixed-used multi-energy systems” [@Klemm.Indicators]. Traditionally, such systems are designed by simulating and comparing a very few predefined energy supply scenarios, without using optimization methods. In addition, individual buildings, consumption sectors, or energy sectors are rarely planned and designed holistically, but rather separately from each other [@Lukszo.2018]. Finally, planning processes are often driven only by financial interests, instead of considering additional planning objectives, such as minimizing greenhouse gas emissions or reducing final energy demands. To fully exploit all synergies and avoid conflicting interests of increasingly entangled energy systems [@Pfenninger.2014], it is necessary to carry out holistic planning [@Lukszo.2018]. Therefore, all energy sectors, planning objectives and an entire spatial entity should be considered within a holistic analysis [@UN.2015]. Thereby, not only certain, but all theoretically possible supply scenarios should be compared by using optimization algorithms [@DeCarolis.2017], to ensure that those scenarios are identified that allow the minimization of the planning objectives by a given ratio [@Klemm.Indicators]. All these demands on planning and optimization methods result in increasingly high computing requirements, especially in run-time and random access memory (RAM) [@Klemm.2023]. To limit the necessary computing capacities to an acceptable extend, modelers must make decisions regarding the temporal and spatial resolution of the system. Alternatively, model-based or solver-based methods can be used, which reduce the computational requirement [@Cao.2019], with only slightly different result quality.

The Spreadsheet Energy System Model Generator (SESMG) is based on the Open Energy Modeling Framework (oemof) [@oemof]. Combined with its own functionalities, the SESMG meets the above described modeling challenges, by

* considering the **multi-energy system (MES)** approach [@Mancarella.2016], 

* carrying out **multi-objective optimization** by using the epsilon-constraint-method [@Mavrotas.2009], and

* enabling high spatial resolution results through the applicability of **model-based** methods for the **reduction of computational effort** [@Klemm.2023].

Therefore, the SESMG enables the optimization of multi-sectoral and spatial synergies of urban energy systems of up to 1000 buildings. Through the multi-criteria result output in the form of a Pareto front, transformation processes between status quo, cost minimized and emission minimized target scenarios can be identified.

Finally, the SESMG comes with several advantages regarding user-friendliness compared to other modeling tools, due to

* applicability without any programming knowledge,

* automatic conceptualization of individual urban energy systems with any size,

* automatic result processing and vizualization of complex relationships in form of system graphs, pareto-fronts, energy amount diagrams, capacity diagrams, and more, as well as

* a set of standard (but still customizable) technical and economic modeling parameters including description and references.

# Projects (?)

An ongoing list of peer review publications, conference proceedings, study works, research projects and more related to the SESMG can be found in the [documentation of the SESMG](https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/05.01.00_publications.html "documentation of the SESMG") **LINK NACH PUBLIKATION AKTUALISIEREN**

# Acknowledgements
The authors would like to thank the oemof user and developer community for the development of the Open Energy Modeling Framework and for discussions regarding the development of the SESMG. This research has been conducted within the R2Q project, funded by the German Federal Ministry of Education and Research (BMBF), grant number 033W102A.

# References

