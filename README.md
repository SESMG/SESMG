# Spreadsheet Energy System Model Generator (SESMG) ![what-why](https://cs.adelaide.edu.au/~christoph/badges/content-what-why-brightgreen.svg) ![how](https://cs.adelaide.edu.au/~christoph/badges/content-how-green.svg)

The **SESMG** provides a spreadsheet interface to the Open Energy Modeling Framework (oemof), allowing modeling and optimization of urban energy systems based a spreadsheet.

**SESMG** makes it easier to create oemof-based energy system models.

- You don't need to touch the command line
- You don't need programming skills
- **SESMG** is an intuitive spreadsheet driven tool

The components defined in this spreadsheet are defined with the included Python 
program and the open source Python library “oemof”, assembled to an energy system 
and optimized with open source solvers, e.g. “cbc”. The modeling results can be 
viewed and analyzed using a browser-based results output.)

![workflow_graph_SESMG](/docs/images/readme/workflow_graph.jpeg")

## Quick Start ![how](https://cs.adelaide.edu.au/~christoph/badges/content-how-green.svg)

### Step 1) Download Python 3.7 ![how](https://cs.adelaide.edu.au/~christoph/badges/content-how-green.svg)

- go to the Python download page
- chose a Python version (e.g., “Python 3.7.6”) and click “download”
- download the operating system specific installer (e.g., “Windows x86-64 executable installer”)
- execute the installer on your computer

Linux only: 
- run `$ sudo update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 2`
- test by running `$ python3 --version`


### Step 2) Download the Spreadsheet Energy System Model Generator from GIT as .zip folder ![how](https://cs.adelaide.edu.au/~christoph/badges/content-how-green.svg)

### Step 3) Extract the .zip folder into any directory on the computer. ![how](https://cs.adelaide.edu.au/~christoph/badges/content-how-green.svg)

### Step 4) Download the CBC-solver (Windows only) ![how](https://cs.adelaide.edu.au/~christoph/badges/content-how-green.svg)

Download ![HERE](http://ampl.com/dl/open/cbc/cbc-win64.zip)

Within this step there are two options: 
- install the cbc-Solver on your whole operating system 
- copy and paste the downloaded executable two your **SESMG**-working directory

### STEP 5) Install Graphviz (Windows only) ![how](https://cs.adelaide.edu.au/~christoph/badges/content-how-green.svg)

Download ![HERE](https://graphviz.gitlab.io/download/)

- select and download the graphviz version for your device (e.g. graphviz-2.38.msi for Windows)
- Execute the installation manager you just downloaded. Choose the following directory for the installation: “C:\Program Files (x86)\Graphviz2.38" (should be the default settings)

### STEP 6) Start the operating system specific installation file. ![how](https://cs.adelaide.edu.au/~christoph/badges/content-how-green.svg)

## Local Development ![how](https://cs.adelaide.edu.au/~christoph/badges/content-how-green.svg)

1. Install Jekyll and plug-ins in one fell swoop. `gem install github-pages` This mirrors the plug-ins used by GitHub Pages on your local machine including Jekyll, Sass, etc.
2. Clone down your fork `git clone https://github.com/yourusername/yourusername.github.io.git`
3. Serve the site and watch for markup/sass changes `jekyll serve`
4. View your website at http://127.0.0.1:4000/
5. Commit any changes and push everything to the master branch of your GitHub user repository. GitHub Pages will then rebuild and serve your website.

## Moar! ![references](https://cs.adelaide.edu.au/~christoph/badges/content-references-orange.svg)

I've created a more detailed walkthrough, [**Build A Blog With Jekyll And GitHub Pages**](http://www.smashingmagazine.com/2014/08/01/build-blog-jekyll-github-pages/) over at the Smashing Magazine website. Check it out if you'd like a more detailed walkthrough and some background on Jekyll. :metal:

It covers:

- A more detailed walkthrough of setting up your Jekyll blog
- Common issues that you might encounter while using Jekyll
- Importing from Wordpress, using your own domain name, and blogging in your favorite editor
- Theming in Jekyll, with Liquid templating examples
- A quick look at Jekyll 2.0’s new features, including Sass/Coffeescript support and Collections

## Jekyll Now Features ![what-why](https://cs.adelaide.edu.au/~christoph/badges/content-what-why-brightgreen.svg) 

✓ Command-line free _fork-first workflow_, using GitHub.com to create, customize and post to your blog  
✓ Fully responsive and mobile optimized base theme (**[Theme Demo](http://jekyllnow.com)**)  
✓ Sass/Coffeescript support using Jekyll 2.0  
✓ Free hosting on your GitHub Pages user site  
✓ Markdown blogging  
✓ Syntax highlighting  
✓ Disqus commenting  
✓ Google Analytics integration  
✓ SVG social icons for your footer  
✓ 3 http requests, including your avatar  

✘ No installing dependencies
✘ No need to set up local development  
✘ No configuring plugins  
✘ No need to spend time on theming  
✘ More time to code other things ... wait ✓!  

## Questions? ![who](https://cs.adelaide.edu.au/~christoph/badges/content-who-yellow.svg) ![references](https://cs.adelaide.edu.au/~christoph/badges/content-references-orange.svg)

[Open an Issue](https://github.com/barryclark/jekyll-now/issues/new) and let's chat!

## Other forkable themes ![references](https://cs.adelaide.edu.au/~christoph/badges/content-references-orange.svg)

You can use the [Quick Start](https://github.com/barryclark/jekyll-now#quick-start) workflow with other themes that are set up to be forked too! Here are some of my favorites:

- [Hyde](https://github.com/poole/hyde) by MDO
- [Lanyon](https://github.com/poole/lanyon) by MDO
- [mojombo.github.io](https://github.com/mojombo/mojombo.github.io) by Tom Preston-Werner
- [Left](https://github.com/holman/left) by Zach Holman
- [Minimal Mistakes](https://github.com/mmistakes/minimal-mistakes) by Michael Rose
- [Skinny Bones](https://github.com/mmistakes/skinny-bones-jekyll) by Michael Rose

## Credits ![who](https://cs.adelaide.edu.au/~christoph/badges/content-who-yellow.svg)

- [Jekyll](https://github.com/jekyll/jekyll) - Thanks to its creators, contributors and maintainers.
- [SVG icons](https://github.com/neilorangepeel/Free-Social-Icons) - Thanks, Neil Orange Peel. They're beautiful.
- [Solarized Light Pygments](https://gist.github.com/edwardhotchkiss/2005058) - Thanks, Edward.
- [Joel Glovier](http://joelglovier.com/writing/) - Great Jekyll articles. I used Joel's feed.xml in this repository.
- [David Furnes](https://github.com/dfurnes), [Jon Uy](https://github.com/jonuy), [Luke Patton](https://github.com/lkpttn) - Thanks for the design/code reviews.
- [Bart Kiers](https://github.com/bkiers), [Florian Simon](https://github.com/vermluh), [Henry Stanley](https://github.com/henryaj), [Hun Jae Lee](https://github.com/hunjaelee), [Javier Cejudo](https://github.com/javiercejudo), [Peter Etelej](https://github.com/etelej), [Ben Abbott](https://github.com/jaminscript), [Ray Nicholus](https://github.com/rnicholus), [Erin Grand](https://github.com/eringrand), [Léo Colombaro](https://github.com/LeoColomb), [Dean Attali](https://github.com/daattali), [Clayton Errington](https://github.com/cjerrington), [Colton Fitzgerald](https://github.com/coltonfitzgerald), [Trace Mayer](https://github.com/sunnankar) - Thanks for your [fantastic contributions](https://github.com/barryclark/jekyll-now/commits/master) to the project!

## Contributing ![contribution](https://cs.adelaide.edu.au/~christoph/badges/content-contribution-blue.svg)

Issues and Pull Requests are greatly appreciated. If you've never contributed to an open source project before I'm more than happy to walk you through how to create a pull request.

You can start by [opening an issue](https://github.com/barryclark/jekyll-now/issues/new) describing the problem that you're looking to resolve and we'll go from there.

I want to keep Jekyll Now as minimal as possible. Every line of code should be one that's useful to 90% of the people using it. Please bear that in mind when submitting feature requests. If it's not something that most people will use, it probably won't get merged. :guardsman:





Examples
-------------
Examples are stored in a separate GIT-Repository:

https://github.com/chrklemm/SESMG_Examples

Documentation
-------------
The `documentation <https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/>`_,
which includes detailed instructions for installation and use, troubleshooting 
and much more, can be accessed via the following link:

https://spreadsheet-energy-system-model-generator.readthedocs.io/en/latest/

Contact
----------------

Münster University of Applied Sciences

Christian Klemm

christian.klemm@fh-muenster.de

Acknowledgements
----------------
The Spreadsheet Energy System Model Generator was carried out within the 
research project `R2Q "Resource Planing for Urban Districts" <https://www.fh-muenster.de/forschungskooperationen/r2q/index.php>`_. 
The project was funded by the BMBF within the framework of the Federal Ministry 
of Education and Research's `RES:Z "Resource-Efficient Urban Districts" <https://ressourceneffiziente-stadtquartiere.de/>`_ funding 
programme. The funding measure is part of the flagship initiative "City of the Future" within the BMBF's framework programme "Research for Sustainable Development - FONA3".
