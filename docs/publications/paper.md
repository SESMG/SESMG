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
    equal-contrib: true
    affiliation: "1, 2"
  - name: Gregor Becker
	orcid: 0000-0001-8803-6873
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
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
 - name: Department of Energy, Building Services and Environmental Engineering,
Münster University of Applied Sciences, Germany
   index: 1
 - name: Department of Energy and Environmental Management, Europa-Universität Flensburg, Germany 
   index: 2
date: 31 March 2023
bibliography: paper.bib

---

# Summary

...

# Statement of need

...

# Mathematics

Single dollars ($) are required for inline mathematics e.g. $f(x) = e^{\pi/x}$

Double dollars make self-standing equations:

$$\Theta(x) = \left\{\begin{array}{l}
0\textrm{ if } x < 0\cr
1\textrm{ else}
\end{array}\right.$$

You can also use plain \LaTeX for equations
\begin{equation}\label{eq:fourier}
\hat f(\omega) = \int_{-\infty}^{\infty} f(x) e^{i\omega x} dx
\end{equation}
and refer to \autoref{eq:fourier} from text.

# Citations

Citations to entries in paper.bib should be in
[rMarkdown](http://rmarkdown.rstudio.com/authoring_bibliographies_and_citations.html)
format.

If you want to cite a software repository URL (e.g. something on GitHub without a preferred
citation) then you can do it with the example BibTeX entry below for @fidgit.

For a quick reference, the following citation commands can be used:
- `@author:2001`  ->  "Author et al. (2001)"
- `[@author:2001]` -> "(Author et al., 2001)"
- `[@author1:2001; @author2:2001]` -> "(Author1 et al., 2001; Author2 et al., 2002)"

# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png)
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements

We acknowledge contributions from Brigitta Sipocz, Syrtis Major, and Semyeong
Oh, and support from Kathryn Johnston during the genesis of this project.

# References
