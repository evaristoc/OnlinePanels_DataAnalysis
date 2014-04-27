The main purpose of this repository is to publicly share a (quick and dirty) code I developed while working for an Online Consumer Panel company (a more elaborated motive explanation will be included soon).

By the time of this proposal, objectives of this work were:
- Evaluating the feasibility of simulations for (strategic) decision making support tools in the online consumer panel industry
- Identify critical points for additional business process automation (eg current sample size analysis) or tools for strategic decision making (eg annual recruitment budget allocation analysis) 
- Introducing to/Testing concepts and dynamics as observed in the field / empirical data

There are two undistinguished simulation exercises in the code:

1) An IBRO (for Inflow - Base - Retention/chrun - Outflow) model
- Sketching an IBRO model and evaluate its programatic feasibility
- Determines the parameters required to create a workable "universe" composed by "panelists" instances with different tenures which final aggregate response rate is that asked by user
- Inflow/Retention/Outflow based on fixed rules
- Preliminary evaluation of the dynamics of the instances' tenure and composition dynamics

2) A simulation of different repeated sampling schemes ("trackers") during a determined period (counted as 'weeks')
- Relies on the creation of a workable "universe" resulting of running the IBRO model
- Calculate the parameters for a repeated sampling to build a "tracker" simulator with replacement subjected to 'time-based elimination rules' (some parameters are exceptional to this work)
- Includes "elimination rules" (those which prevent instances that will be still in the universe not to be available for sampling after a determined number of iterations)
- Formulate a 2x2 experiment based on the parameter used to calculate sample size (usually an aggregate "response rate", 2 different calculations) and "weekly" fieldwork period (fixed or random with maximum)
- Focuses on cost-efficiency analysis of different tracker simulations

The project was followed by a more concrete proposal and further analyses of empirical data (not included here)

Observations:
- For being a 'quick and dirty' sketching demo the code is still "unpolished"
- The demo doesn't have a GUI or similar (runs on IDLE or command prompt); there are sections where parameters must be changed manually on the code
- Data / dynamics were based on sketched models and or arbitrary parameters
- An external file was used to assign response rates to panelist instances; file included in the repository

Participants:
E Caraballo, conception and developer; L Borja, (internal) business developer (LSR)
