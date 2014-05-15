ONLINE PANEL SIMULATION - SECOND PHASE - Outline

This script is more advanced than the previous phase, and although won't easily scale to a large amount of records without affecting performance, the use of OO approach will ease readability, possible extensions and improvements, and the maintenance of the current script.

A first (still uncompleted) script file was loaded:
- the script gives an idea of the direction of the major implementation
- differently to previous phase, during this phase the project uses Object Oriented programming as main programming paradigm, which is more suitable to the model characteristics 

Keeping the same objectives as in the first phase, in this second phase I will continue exploring the simulation. This time subsequent functions, behaviours and attributes will be added to better fit some current real practices but also some simplifications. The IBRO model (see previous phase) could be emphasised but the general approach to sampling will be modified and upgraded to include certain dynamics found in field.
Some observations are:

1. IBRO (for Inflow - Base - Retention/churn - Outflow) model

- Functions better supported by empirical observations to explain survival and response rates per cohort will be used.
- The baseline for a population would be evaluated in terms of a year-time-horizon proposal, counted in weeks (not days, as previous phase).

2. Sampling Simulations

- Previous simulation was based on an invitation model of "one invite, one survey". For this phase the now more popular Inbox and Router models will be suggested. This may involve a new class or method to simulate the Inbox per panelist.
- For the moment the sampling analysis and the behaviour of the population during the sampling event will be evaluated in weeks, no days as in Phase 01.
- So far the simulated surveys will consist only in ad-hoc ones, but this could be easily modified to include simulations for longitudinal studies of any kind, as well as exclusions.

EDIT 15-05-2014:

A first quick test of the currently available classes and functions has been included.

Apart of what it is shown, additional tasks would include:
- Rescuing the concept of "exposure rate" given in the previous definition as a black-box measure approximation to the effects of technological change
- Simple Diagrams of the simulations (currently unavailable)
- A threading procedure for the sampling Event
- Likely also a threading for the universe generation during updating of Panellist's instances status

PS: Phases 01 and 02 are working as the base to investigate the details of relevant behaviours and parameters. A possible third phase would re-evaluate the results and parameters found at phases 01 and 02 seeking a simplified scalable model to reproduce more data-intensive simulations.  
PSS: Currently thinking about creating a web-based interface to interact with the model instead... 

Participants: E Caraballo, conception and developer







