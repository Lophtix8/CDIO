# Project Plan

## Introduction 
The design of new materials with desired properties is a crucial step in making innovative technologies viable. A typical challenge in materials design is to find materials that fulfill specific requirements on efficiency, cost, environmental impact, length of life, safety, and other properties. Theoretical investigation of hypothetical material candidates and system configurations by computational materials simulations have become a standard tool in this field. These simulations help us understand the physics of materials and systems of molecules and can be used to predict many different materials properties. The continued progression of computational power, storage capability, and improved methodology, has led to the application of these methods in high-throughput to produce large, openly available, databases of theoretically predicted materials properties that are a major asset for addressing materials design challenges.

This program means to preform a material dynamic simulation on an array of materials with a selected number of degrees of freedom. The data extracted from the simulation will then be analyzed to find relevant trends. The main simulation will consist of forces applied to a bulk material to simulate a stress on the material causing it to fracture. Thus, the strength and toughness of different materials can be studied, to find what makes a material exhibit properties that keep it from fracturing.


## Program schematic
<img src="images/schematic.png" alt="MarineGEO circle logo" style="height: 500px; "/>

## Roadmap
The project will be divided in to tree (possibly overlapping) phases. The "Build and setup phase", the "Material simulation phase" and the "Data analysis and plotting phase". These are also depicted in the program schematic.

### Milestones
A few of the milestones in the project are listed below, with reservation to add more, or change eisting ones further on in the project.
- Inputting a config-file and getting an output in the form of a supercell,
- simulating a tear in a bulk material and
- finishing the final report

### Backlog
Below is a list of the backlog for the project, divided into epics, and some of their stories. Each story will be divided into tasks which are left as undetermined at this stage of the project. The stories are only outlined, with reservation to changes further ahead in the project.

#### Build and setup
This epic contains everything that is needed to initialize a simulation. Here, all data preparation, creation and deletion of a simulation cell, setting up the main workflow of the whole product, etc. Stories include:
- Create a main-function that runs the entire program,
- create a function that builds a supercell,
- create a function that deletes old supercells that have already been simulated.

#### Molecular dynamics simulation
The molecular dynamics (MD) part of the project is the part that runs the actual simulations. This is what will be queued up at the supercomputers. Stories include:
- Create a workflow-function that decides how the MD-simulation will be performed,
- create an MD funcion,
- create a function that saves relevant data from an MD run.

#### Data analysis
This is the last part of the program, as well as the development. In this part of the program all data that has been saved from the MD-runs of different materials will be analyzed, both individually and against each other. Stories include:
- Create a data analysis-function that compiles relevant data from MD-simulations,
- create a plotting function that visualizes the compiled data in a relevant way.



