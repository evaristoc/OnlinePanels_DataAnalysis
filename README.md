The main purpose of this repository is to publicly share a (quick and dirty) code I developed while working for an Online Consumer Panel company (a more elaborated motive explanation will be included soon).

Results of this work were used to:
- Evaluate the feasibility of simulations for strategic decision making in the online consumer panel industry
- Introduce to/Test concepts and dynamics as observed in the field as well as empirical data 
- Sketch an IBRO model and evaluate its programatic feasibility
- Sketch an analytical tool for fieldwork simulation of sometimes called "tracking" studies, with focus on cost-efficiency analysis

There are two undistinguished simulation exercises in the code:

1) An IBRO (inflow - base - retention/chrun - outflow) model
*** Determines the parameters required to create a workable "universe" composed by "panelists" instances with different tenures which final aggregate response rate is that asked by user
*** Inflow/Retention/Outflow based on fixed rules

2) A simulation of different repeated sampling schemes ("trackers") during a determined period (counted as 'weeks')
*** This section relies on the creation of a workable universe after running the previous IBRO model
*** Works on the parameters for a repeated sampling (some parameters are exceptional to this work)
*** Establishes the elimination rules (instances that will be still in the universe but not available for sampling after a determined number of iterations)
*** Formulate 2x2 experiment based on the parameter used to calculate sample size (usually a "response rate", 2 different parameters) and "weekly" fieldwork period (fixed or random with maximum)

The project was followed by a more concrete proposal and further analyses of empirical data with valuable results (not included here)

Caveats:
- For being a 'quick and dirty', sketching demo, the project is still unfinished
- The demo doesn't have a GUI or similar (runs on IDLE or command prompt); there are sections where parameters must be changed manually on the code
- There is substantial use of arbitrary models or data that "simulated" observations in the field
- There is an external file used to evaluate the response rates to be assigned to the panelist instances (included in the repository)

Participants:
E Caraballo, conception and developer
L Borja, (internal) business developer (LSR)
