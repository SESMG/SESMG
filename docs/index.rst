The Spreadsheet Energy System Model Generator 
=================================================

What is the SESMG?
-------------------------

The Spreadsheet Energy System Model Generator (SESMG) is a tool for modeling and optimizing energy systems with a focus on urban systems. The SESMG is easily accessible as it comes with a browser-based graphical user interface, spreadsheets to provide data entry, and detailed documentation on how to use it. **Programming skills are not required** for the installation or application of the tool. The SESMG includes **advanced modeling features** such as the application of the **multi-energy system (MES)** approach, **multi-objective optimization**, model-based methods for **reducing computational requirements**, and **automated conceptualization and result processing** of urban energy systems with high spatial resolution. Due to its accessibility and the applied modeling methods, urban energy systems can be modeled and optimized with comparatively low effort. [#FN1]_


.. figure:: images/SESMG_principle.png
   :width: 100 %
   :alt: SESMG_principle.png
   :align: center

   From an input spreadsheet to interactive modeling results: The Spreadsheet Energy System Model Generator


Why is the SESMG useful?
-------------------------------

The Spreadsheet Energy System Model Generator (SESMG) meets various challenges of modeling urban energy systems. Planning and optimizing the design of urban energy systems is becoming increasingly complex [1] due to sector coupling, the use of decentralized renewable energy sources with volatile production, the use of diverse energy storage systems, the growing importance of new energy sectors such as hydrogen, as well as the increasing relevance of multiple planning objectives. In this context, urban energy systems are defined as “the combined process of acquiring and using energy in a given spatial entity with a high density and differentiation of residents, buildings, commercial sectors, infrastructure, and energy sectors (e.g., heat, electricity, fuels)” [2]. Traditionally, such systems are designed by simulating and comparing a limited number of pre-defined energy supply scenarios without using optimization methods. Individual buildings, consumption sectors, or energy sectors are rarely planned and designed holistically, but rather separately from each other [3]. Finally, planning processes are often only driven by financial interests, rather than considering additional planning objectives such as minimizing green house gas (ghg) emissions, or final energy demand. To fully exploit all synergies and to avoid conflicting interests due to interdependencies of increasingly entangled energy systems [4], it is necessary to carry out holistic planning [3]. Therefore, all energy sectors, planning objectives, as well as an entire spatial entity should be considered within a holistic analysis [5]. Not only certain, but all theoretically possible supply scenarios should be compared by using optimization algorithms [6] in order to ensure that scenarios that allow the minimization of the planning objectives by a given ratio are identified [2]. All these requirements for planning and optimization methods result in increasingly high computing requirements, especially in run-time and random access memory (RAM) [7]. To limit the necessary computing capacities to an acceptable extend, modelers may make decisions regarding the temporal and spatial resolution of the system. Alternatively, model-based or solver-based methods can be used to reduce the computational requirements [8], with only slight differences in the quality of the results.

Combining functions of the underlying Open Energy Modeling Framework (oemof) [9] as well as its own functionalities, the SESMG overcomes these typical problems of modeling urban energy systems by

* considering the **multi-energy system (MES)** approach [10],

* carrying out **multi-objective optimization** by using the epsilon-constraint-method [11], and by

* enabling high spatial resolution results through the applicability of **model-based** methods for the **reduction of computational effort** [7].

The SESMG enables the optimization of multi-sectoral and spatial synergies of entire urban energy systems with an adaptable number of buildings. Due to the multi-criteria results in the form of a Pareto front, transformation processes between status quo, financial cost minimized and ghg emission minimized target scenarios can be identified.

The target group of the SESMG are (urban) energy system planners and researchers in the field of energy engineering. As it is required for the application of the SESMG and the interpretation of the results, users must have a certain basic knowledge of energy systems and energy engineering. Compared to other tools for the modeling and optimization of urban energy systems the SESMG provides several advantages regarding user-friendliness due to

* being available under an **open-source license**,

* applicability **without any programming knowledge**,

* **automatically conceptualizing** individual urban energy systems of any size,

* **automatic result processing and visualization** of complex relationships in form of system graphs, Pareto fronts, energy amount diagrams, and more, as well as

* a broad set of **standard (but still customizable) technical and economic modeling parameters** including description and references.

The SESMG comes with a detailed documentation, including step-by-step instructions, explanations of all modeling methods, and troubleshooting with known application errors. In addition, the documentation includes an ongoing list of peer review publications, conference proceedings, study works, research projects, and other publications related to the SESMG. [#FN1]_


How is the documentation structured?
-------------------------------------

This documentation consists of the following sections:

Modeling Methods
^^^^^^^^^^^^^^^^

The modeling methods section contains general basics for modeling energy systems and explanations of the modeling methods used in the SESMG.

* :doc:`01.01.00_structure_of_energy_systems`
* :doc:`01.02.00_multi_criteria_optimization`
* :doc:`01.03.00_model_simplification`
* :doc:`01.04.00_urban_district_upscaling`
	
	
..	toctree::
	:maxdepth: 3
	:hidden:
	:caption: Modeling Methods
	
	01.01.00_structure_of_energy_systems
	01.02.00_multi_criteria_optimization
	01.03.00_model_simplification
	01.04.00_urban_district_upscaling
	
	
Manual
^^^^^^
The manual section contains detailed instructions on how to install and apply the different modeling methods. New users are recommended to start with the installation, get used to the basic functionalities of the interface and follow the given examples.

* :doc:`02.01.00_installation`
* :doc:`02.02.00_application`
* :doc:`02.02.01_interface`
* :doc:`02.02.02_model_definition`
* :doc:`02.02.03_urban_district_upscaling`
* :doc:`02.02.04_results`
* :doc:`02.02.05_technical_data`
* :doc:`02.02.06_examples`
* :doc:`02.03.00_demo`
* :doc:`02.04.00_additional_features`
	
	
..	toctree::
	:maxdepth: 3
	:hidden:
	:caption: Manual
	
	02.01.00_installation
	02.02.00_application
	02.03.00_demo
	02.04.00_additional_features


Troubleshooting
^^^^^^^^^^^^^^^

The troubleshooting consists of known errors during the installation and modelling process and how they can be solved.

* :doc:`03.00.00_trouble_shooting`
	

..	toctree::
	:maxdepth: 2
	:hidden:
	:caption: Troubleshooting
	
	03.00.00_trouble_shooting


Sourcecode Documentation
^^^^^^^^^^^^^^^^^^^^^^^^

The source code documentation describes the individual python functions of the SESMG. This part of the documentation is primarily intended for users who want to contribute to the further development of SESMG.

* :doc:`04.00.00_sourcecode_documentation`

..	toctree::
	:maxdepth: 3
	:hidden:
	:caption: Sourcecode Documentation
	
	04.00.00_sourcecode_documentation
	

Further Information
^^^^^^^^^^^^^^^^^^^^^^^^^
Further information related to the SESMG is listed here.

* :doc:`05.01.00_publications`
* :doc:`05.02.00_related_links`
* :doc:`05.03.00_citation`
* :doc:`05.04.00_license`
* :doc:`05.05.00_contact`
* :doc:`05.06.00_contributors`
* :doc:`05.07.00_acknowledgements`
		
..	toctree::
	:maxdepth: 2
	:hidden:
	:caption: Further Information 
	
	05.01.00_publications
	05.02.00_related_links
	05.03.00_citation
	05.04.00_license
	05.05.00_contact
	05.06.00_contributors
	05.07.00_acknowledgements

References
-----------

[1] Zhang, X., Lovati, M., Vigna, I., Widén, J., Han, M., Gal, C., & Feng, T. (2018). A review of urban energy systems at building cluster level incorporating renewable-energy-source (RES) envelope solutions. Applied Energy, 230, 1034–1056. https://doi.org/10.1016/j.apenergy. 2018.09.041

[2] Klemm, C., & Wiese, F. (2022). Indicators for the optimization of sustainable urban energy
96 systems based on energy system modeling. Energy, Sustainability and Society, 12(1), 3. https://doi.org/10.1186/s13705-021-00323-3

[3] Lukszo, Z., Bompard, E., Hines, P., & Varga, L. (2018). Energy and Complexity. Complexity, 2018, 1–2. https://doi.org/10.1155/2018/6937505

[4] 111 Pfenninger, S. (2014). Energy systems modeling for twenty-first century energy challenges. Renewable and Sustainable Energy Reviews, 33, 74–86. https://doi.org/10.1016/j.rser.2014.02.003

[5] 114 United Nations Environment Programme. (2015). District energy in cities: Unlocking the potential of energy efficiency and renewable energy. https://we116docs.unep.org/20.500.11822/9317; UNEP.

[6] DeCarolis, J., Daly, H., Dodds, P., Keppo, I., Li, F., McDowall, W., Pye, S., Strachan, N., Trutnevyte, E., Usher, W., Winning, M., Yeh, S., & Zeyringer, M. (2017). Formalizing best practice for energy system optimization modelling. Applied Energy, 194, 184–198. https://doi.org/10.1016/j.apenergy.2017.03.001

[7] Klemm, C., Wiese, F., & Vennemann, P. (2023). Model-based run-time and memory reduction for a mixed-use multi-energy system model with high spatial resolution. Applied Energy, 334, 120574. https://doi.org/10.1016/j.apenergy.2022.120574

[8] Cao, K.-K., von Krbek, K., Wetzel, M., Cebulla, F., & Schreck, S. (2019). Classification and evaluation of concepts for improving the performance of applied energy system optimization models. Energies, 12(24), 4656. https://doi.org/10.3390/en12244656

[9] Krien, U., Kaldemeyer, C., Günther, S., Schönfeldt, P., Simon, H., Launer, J., Röder, J., Möller, C., Kochems, J., Huyskens, H., @steffenGit, Schachler, B., Pl, F., Sayadi, S., Duc, P., Endres, J., Büllesbach, F., Fuhrländer, D., @gplssm, Francesco, W., Kassing, P., Zolotarevskaia, E., Berendes, S., Lancien, B., Developer, A., Developer, A., Developer, A., Schürmann, L., Developer, A., Delfs, J., Developer, A., Developer, A., Smalla, T., Developer, A., Wolf, J., Developer, A., Gaudchau, E., Developer, A., & Rohrer, T. oemof.solph [Computer software]. https://doi.org/10.5281/zenodo.596235

[10] Mancarella, P., Andersson, G., Pecas-Lopes, J. A., & Bell, K. R. W. (2016). Modelling of integrated multi-energy systems: Drivers, requirements, and opportunities. 2016 Power Systems Computation Conference (PSCC), 1–22. https://doi.org/10.1109/PSCC.2016. 7541031

[11] Mavrotas, G. (2009). Effective implementation of the 𝜖-constraint method in Multi-Objective Mathematical Programming problems. Applied Mathematics and Computation, 213(2), 455–465. https://doi.org/10.1016/j.amc.2009.03.037


.. [#FN1] This section was taken in slightly modified form from the following SESMG publication: Klemm, C., Becker, G., Budde, J., Tockloth, J. & Vennemann, P. The Spreadsheet Energy System Model Generator (SESMG): A tool for the optimization of urban energy systems. The Journal of Open Source Software (under review)(2023).
