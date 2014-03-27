##!/usr/bin/env python
#Python 3.2 on Microsoft OS
#Also for Python 3.3
# CLASSES

#global variables

max_indid = [-1]
divisor_beta_1 = [-1,-1]
divisor_beta_2 = [-1,-1]
amount_topurge = -1
wished_rr = .28
univ = [None]
purged = [None]
week = 0
exposure_rate = 0
pbe = 0

class Panelist3(object):
        '''
        # Definition of attributes of a "panelist"
        # Attributes are defined in terms of response and panel life cycle characterisation
        # Additional attributes could be added
        '''
        def __init__(self, indid = -1):
                self.indid = indid
        def recruit (self, recruit = None):
                self.recruit = recruit
        def pstatus(self, pstatus = None):
                self.pstatus = pstatus
        def qstatus(self, qstatus = None):
                self.qstatus = qstatus
        def participation(self, participation = {}):
                self.participation = participation
        def rr(self, rr = None):
                self.rr = rr
        def beta(self, beta):
                self.beta = beta
        def elimstatus(self, elimstatus):
                self.elimstatus = elimstatus
        def purged(self, purged = None):
                self.purged = purged
        def batch(self, batch):
                self.batch = -77

class counter():
        '''
        # A simple counter
        # It would be relevant at different stages for different methods of the Panelist3 class
        # E.g. at the sampling section when imposing elimination rules (period of not allowed sampling)
        '''
        def __init__(self, start):
                self.state = start
        def __call__(self, week):
#         print(week, self.state) #apparently modifies stdout!!!
                if self.state:
                        self.state -= 1
                if self.state == 0:
                        self.state = None

import sys, os
import random
import inspect
import csv
import sqlite3
#
#
# File preparation area, databases are not included here

#filename = 'db_test_01'
#db_test = connect(os.getcwd()+'/'+filename)
#cursor = db_test.cursor()
file_exposure = open(os.getcwd()+'/simulation/files/exposure01.csv','w',newline = '')
csv_exposure = csv.writer(file_exposure, delimiter=' ')
csv_exposure.writerow(['iteration', 'exposure_rate', 'final_prop_qf', 'final_count_qf'])
file_universe = open(os.getcwd()+'/simulation/files/universe01.csv', 'w', newline = '')
csv_universe = csv.writer(file_universe, delimiter=' ')
csv_universe.writerow(['experiment', 'iteration','indid', 'pan_rr', 'beta_origin', 'recruiting','week','qstatus','elimstatus.state'])
file_eligible = open(os.getcwd()+'/simulation/files/eligible01.csv', 'w', newline = '')
csv_eligible = csv.writer(file_eligible, delimiter=' ')
csv_eligible.writerow(['experiment', 'iteration','indid','week', 'sample_pull','qstatus','elimstatus.state'])
file_fieldwork = open(os.getcwd()+'/simulation/files/fieldwork01.csv', 'w', newline = '')
csv_fieldwork = csv.writer(file_fieldwork, delimiter=' ')
csv_fieldwork.writerow(['experiment', 'iteration', 'indid','week', 'sample_pull', 'batch', 'day', 'qstatus','elimstatus.state','participation','purging'])
file_summaries = open(os.getcwd()+'/simulation/files/summary01.csv', 'w', newline = '')
csv_summaries = csv.writer(file_summaries, delimiter=' ')
csv_summaries.writerow(['experiment', 'iteration', 'week', 'universe', 'rr_univ', 'rr_sample_previous', 'beta1uni', 'beta2uni', 'olduni', 'newuni', 'leguni', 'nonleguni', 'eligible', 'rr_eli', 'beta1eli', 'beta2eli', 'oldeli', 'neweli', 'legeli', 'nonlegeli', 'target', 'sample', 'rr_sample', 'sample_pull', 'daysinfieldwork', 'completes', 'quotaful', 'other', 'beta1samp', 'beta2samp', 'oldsamp', 'newsamp', 'legsamp', 'nonlegsamp'])
file_summaries2 = open(os.getcwd()+'/simulation/files/summary02.csv', 'w', newline = '')
csv_summaries2 = csv.writer(file_summaries2, delimiter=' ')
csv_summaries2.writerow(['experiment', 'iteration', 'week', 'universe', 'rr_univ', 'rr_sample_previous', 'rr_BOR', 'rr_average_fw', 'beta1uni', 'beta2uni', 'olduni', 'newuni', 'leguni', 'nonleguni', 'eligible', 'rr_eli', 'beta1eli', 'beta2eli', 'oldeli', 'neweli', 'legeli', 'nonlegeli', 'target', 'sample', 'rr_sample', 'rr_sample_2', 'sample_pull', 'daysinfieldwork', 'completes', 'quotaful', 'other', 'beta1samp', 'beta2samp', 'oldsamp', 'newsamp', 'legsamp', 'nonlegsamp'])

### TODO? COUNT IN interviewing_sample the number of quotafulls and other statuses too? Add to summaries


# FUNCTIONS

def rr_data_preparation(filename):
        '''
        # For this demo the response rate (rr) is an attribute assigned to every new Panelist3 instance
        # We assume we don't know the rr of the Panelist3 but we do know the rr probability distribution
        # For this demo, a separate file with that distribution was read and keep in memory for further changes below in the script
        '''
        in_file = open(filename)
        a = []         #annexing existing values of beta function to a list
        total_length = 0
        while True:
                line = in_file.readline()
                if not line: break
                freq = int(float(line.split()[2][:3])*100)
                a.append(freq)
                total_length += freq
# print(total_length)
        in_file.seek(0)                #annexing existing probabilities as in the file to a list
        b = []
        while True:
                line = in_file.readline()
                if not line: break
                b.append(float(line.split()[1]))
        in_file.close()                 #closing file
        #creating 2 beta function lists (one the opposite of the other)
        beta_1 = [0 for i in range(total_length)]
        beta_2 = [0 for i in range(total_length)]
        beta_index = 0
        for index, freq in enumerate(a):
                if freq != 0:
                        count = 0
                        while count <= freq:
                         if beta_index == total_length: break
                         beta_1[beta_index] = b[index]
                         beta_2[beta_index] = 1-b[index]
                         beta_index +=1
                         count += 1
                        else:
                         beta_1[beta_index] = 0
                         beta_2[beta_index] = 0
                         beta_index += 1
        return beta_1, beta_2

### GLOBAL FILE BETA rr
in_file = os.getcwd()+'/simulation/lower_rr.txt'
beta_1, beta_2 = rr_data_preparation(in_file)

## The following algorithm keeps the same amount of panelists all the time
def purging_f(univ, purged, week):
        '''
        # The purging function (selecting Panelist3 instances that would not be more part of panel so they won't be invited any more
        # It is a simple garbage collector
        # The function for this demo was thought as a relatively simple rule based on:
        - (fixed) amount of instances to be garbage collected
        - longevity of the instance
        - assigned response rate of the instance

        # Other rules apply when not finding to fill the fixed amount
        '''
        count_purging = 0
# Purge panelists up to amount according to numeric order in the universe list and against panelist rr
        for topurge in univ:
                if count_purging == amount_topurge: break
                bernoulli_purged = random.random()
                if bernoulli_purged >= topurge.rr:
                        #print(i.indid, bernoulli_purged, i.rr)
                        topurge.purged(week)
                        purged.append(topurge)
                        univ.remove(topurge)
                        count_purging += 1
# If at the end of the previous purge the amount_topurge is not reached, then just purge a random sample of size equal to remaining amount_topurge
        if count_purging < amount_topurge:
                purgedsample = random.sample(univ,amount_topurge-count_purging)
                for topurge in univ:
                        if topurge in purgedsample:
                         topurge.purged(week)
                         purged.append(topurged)
                         univ.remove(topurge)

def new_recruits_f(univ, size, week, proportion_beta = 0.85):
        '''
        # This function generates a (fixed) amount of Panelist3 instances at every fixed period of time (week)
        # The section also determines an initial probability distribution of the response rate (rr) attribute at the moment of recruitment
        # Although the assignment of a rr attribute for each instance is unknown,
        we assume we do know the expected probability distribution of the rr in the recruited sub-population
        '''
        new_recruits = [new+1+max_indid[0] for new in range(size)]
        for new in new_recruits:
                added_panelist = Panelist3(new)
                bernoulli = random.random()
                if bernoulli <= proportion_beta:
                        added_panelist.rr(random.choice(beta_1)/random.choice(divisor_beta_1)) # reducing the entry values of rr
                        added_panelist.beta(1)
                else:
                        added_panelist.rr(random.choice(beta_2)/random.choice(divisor_beta_2))
                        added_panelist.beta(2)
                added_panelist.recruit(week)        
                #capturing max_indid
                univ.append(added_panelist)

def rr_calc(univ):
        '''
        # Calculates the response rate for a list of Panelist3 instances
        '''
        added_rr = 0
        total_rr = 0
        for i in univ:
                added_rr += i.rr
        if len(univ):
                total_rr = added_rr/len(univ)
        else:
                total_rr = 0
        return total_rr

        
#Will refer to the rr distributions of the new recruitments! so we can get an expected wished average rr!!!!
def parameters_univ(weeks, proportion_beta_est):
        '''
        # This function will calculate the initial parameters of entry so the baseline could reach the required overal response rate at the end of a fixed period
        # There were also other fixed parameters to facilitate the processing of data
        # In fact this is bit more complex than a baseline: an iteration process was proposed to find the values of the composition of response rates attributed to Panelist3 instances until reaching a composition which in aggregate reflect the expected response rate of the population;
        # Each searching iteration consists of 200 ones of purging/recruitment
        # The process seems robust but slow and takes time for low expected values of desired (universe) response rate



        # IMPORTANT: The first is to estimate a desired overall response rate for a universe
        # This will affect the composition of the panel, as we require to reach an equilibrium of recruitment/purging
        # values so the resulting response rate keeps the same for subsequent updates of the universe when starting the sampling
        # The baseline function will run until reaching the expected value by vary the values of recruitment and purging
        # It is an (brute force) optimisation procedure
        # See the rationale in the functions above
        '''
        while True:
                amount_topurge = 1300##!/usr/bin/env python

                univ = []
                purged = []
                max_indid = [-1]
                week = int(weeks)*(-1) - 200
                replica_data = []
                numavgweek = 0
                #first universe
                new_recruits_f(univ, 6700, week, proportion_beta = proportion_beta_est)
                max_indid = [univ[-1].indid]
                pre_univ_rr = rr_calc(univ)
                print(len(univ), pre_univ_rr)
                sum_rr_calc = 0
                ave_rr_calc = 0
                initial_week = abs(week)
                for count_week in range(initial_week):                 # OJO: parameter for deciding how long the baselining lasts
                        week += 1
                        purging_f(univ, purged, week)
                        new_recruits_f(univ, amount_topurge, week, proportion_beta = proportion_beta_est)
                        max_indid = [univ[-1].indid]
                        replica_data.append((len(univ),rr_calc(univ), week))
                if int(week*0.1) == 0:
                        numavgweek = -1
                else:
                        numavgweek = int(week*0.1)                                                #OJO: to work correctly here, the value of week must be <= 0!!!
                for data in replica_data[numavgweek:]:
                        sum_rr_calc += data[1]
                ave_rr_calc = sum_rr_calc/abs(numavgweek)
                print('ave_rr_calc: ', str(ave_rr_calc)[:5], 'wished_rr: ', str(wished_rr)[:5], 'ave_rr_calc - wished_rr: ', str(ave_rr_calc - wished_rr)[:5])
#                OJO: the calculation of this if...else reminds a Markov inequality: P(k<|X|) <= E[X]/k, creating a superior bound...
                if abs(ave_rr_calc - wished_rr) <= wished_rr*.05: break
                else:
#                in this case: p(X) related to Uni(beta_1)*Ber(proportion_beta_est)/[(wished_rr-0.285)*6/-0.21]+Uni(beta_2)*Ber(1-proportion_beta_est)
#                OJO: the following if...elif is Newton-like method, but with y2 = y1+y1*(mhu(X) - E(X))
#                I know also that |ave_rr_calc - wished_rr| has a min when equal 0, having wished_rr as mhu
#                The objective is to calculate the value of the Ber function
#                OBS: this is a TIME dependent function!!!
                        if ave_rr_calc - wished_rr < 0: proportion_beta_est += proportion_beta_est*(ave_rr_calc - wished_rr)
                        elif ave_rr_calc - wished_rr > 0: proportion_beta_est += proportion_beta_est*(ave_rr_calc - wished_rr)
                print(len(univ), rr_calc(univ))
        return proportion_beta_est, ave_rr_calc, (wished_rr-0.285)*6/-0.21        

        
def creating_baseline_univ(week, pbe, allow_unireport = None):
        '''
        # This section works a baseline pre-simulation of a panel formation in a fixed period of time
        # The underlying assumption is that we would be better off by creating the current universe (the panel) by a repeated process of recruitments and purgings, such as it happened for the large majority of consumer panels
        # In this way we look for guaranteeing a panel composition equivalent to its equivalent empirical form
        # In particular, one important issue here was how to model the longevity component (a pseudo-definition of loyalty)
        '''
        if week > 0: week *= -1
        new_recruits_f(univ, 6700, week, proportion_beta = pbe)
        if allow_unireport:
#UNI_Report
                for panelist in univ:
                        csv_universe.writerow([-77, -77, panelist.indid, str(panelist.rr)[:5],panelist.beta, panelist.recruit, week, -77, -77])
        #capturing max_indid
        max_indid = [univ[-1].indid]
        pre_univ_rr = rr_calc(univ)
        print(len(univ), pre_univ_rr)
        initial_week = abs(week)
        for count_week in range(initial_week):                 # OJO: parameter for deciding how long the baselining lasts
                week += 1
                purging_f(univ, purged, week)
                new_recruits_f(univ, amount_topurge, week, proportion_beta = pbe)
                max_indid = [univ[-1].indid]
        print(len(univ), rr_calc(univ))


#start sampling - run elimination
def eligible(univ):
        '''
        # An eligible is a section of##!/usr/bin/env python
		the universe that can be subjected to sampling at a particular period of time
        # In this case, the eligible includes all panelists but those that are still under an elimination rule
        # This section will take the universe and will inspect those who are still not available for sampling (see more below)
        '''
        eli = []
        for eli_panelist in univ:
                if inspect.ismethod(eli_panelist.qstatus) == True or eli_panelist.qstatus == None:
                        eli.append(eli_panelist)
        return eli


def sampling(rr_type, eli, univ, target, rr, ir, batching = 0):
        '''
        # The sampling procedure takes business rules for selecting those who can participate in a survey program, given an expected response rate

        # For this project there are also additional rules to manipulate some simple exceptions when the expected number of participants is not reached with the previous rule
        '''
        n = target
        if rr_type == 2: ir = 0
        corrected_target = int(n+n/(rr-rr*ir))
        if eli:
                if target >= 5:
                        if int(target/(rr-rr*ir)) < len(eli):
                                sample = random.sample(eli, int(target/(rr-rr*ir)))
                        else:
                                sample = eli
                if target < 5:
                        if int(corrected_target/(rr-rr*ir)) < len(eli):
                                sample = random.sample(eli, int(corrected_target/(rr-rr*ir)))
                        else:
                                sample = eli
        else:
                sample = eli
        if batching:
                for panelist in sample:
                        panelist.batch = random.choice([x+1 for x in range(batching)])
        return sample




def run_elimination(univ, week):
        '''
        # Run the elimination and update attributes
        '''
        for elim in univ:
                if inspect.ismethod(elim.recruit):
                        elim.recruit = week
                if inspect.ismethod(elim.elimstatus):         #if having still a state, discount
                        elim.elimstatus = counter(None)
                if elim.elimstatus.state == None:
                        elim.qstatus = None
                if elim.qstatus:
                        elim.elimstatus(week)


def test_participation(test):
        x = -77
        if not inspect.ismethod(test.participation):
                x = test.participation['day']
        return x##!/usr/bin/env python




def numeric_qststatus(test):
        '''
        # For the client we presented this demo, statuses were better understood if presented according business rules
        # This just converted into numeric for better manipulation
        # Statuses is an attribute that describe the response of the Panelist3 instance to a survey
        # This can be no response (L), completed survey (C), completed but it is over the desired quota (QF) or other status (O)
        '''
        qstatusnum = None
        if inspect.ismethod(test.qstatus): qstatusnum = None
        if test.qstatus == 'L': qstatusnum = 1
        if test.qstatus == 'O': qstatusnum = 2
        if test.qstatus == 'C': qstatusnum = 3
        if test.qstatus == 'QF': qstatusnum = 4
        return qstatusnum




# start sampling - using the last universe for sampling, using the same rr of the universe to calculate size
def interviewing_sample(week, sample_pull, day, remaining_interviews, exposure_rate, ir, interviews, values = [4,28,8]):
        '''
        # The following function models the interviewing process
        # The process is simplified
        # It takes the sample (see above) and subject each selected Panelist3 instance to a chain of probability rules
        # The underlying assumption is that we don't know which instance will get which status but we have an idea of the probability distribution of statuses which is faced against the rr attribute of the Panelist3 instance based on
        empirical evidence or business rules
        '''
        week = week
        count_interviews = 0
        value = 0
        for interviewed in interviews:
                interviewed.qstatus = 'L'
                value = values[0]
                bernoulli_days = random.random()
                if bernoulli_days <= exposure_rate:
                        bernoulli_rr = random.random()
                        if bernoulli_rr <= interviewed.rr:
                                bernoulli_otherstatus = random.random()
                                if bernoulli_otherstatus <= ir:
                                        interviewed.qstatus = 'O'
                                        value = values[1]
                                elif bernoulli_otherstatus > ir and count_interviews < remaining_interviews:
                                        interviewed.qstatus = 'C'
                                        value = values[1]
                                        count_interviews += 1
                                elif bernoulli_otherstatus > ir and count_interviews >= remaining_interviews:
                                        interviewed.qstatus = 'QF'
                                        value = values[2]
                interviewed.elimstatus = counter(value)
                if inspect.ismethod(interviewed.participation):
                        interviewed.participation()
                interview_st = dict(week=week, sample_pull=sample_pull, day=day, status=interviewed.qstatus)
                interviewed.participation.update(interview_st)                
                if interviewed.qstatus in ('O','C','QF'):
                        interviews.remove(interviewed)
        return count_interviews




        
def trackering2(experiment, iteration, num_weeks, week_target, ir, dist_fw, corrector = 1, rr_sample = 0, daysinfieldwork_rr = [], rr_type = 1, no_extra = None, batches = None):
        '''
        # This is a simulation of a suggested longitudinal study fieldwork process based on simple rules obtained from empirical data
        # The trackering function will
        - update the universe at any stage (including purging),
        - update the eligible,
        - sample from that eligible (including some exception handling),
        - update the counter attributes when applicable
        # Process was designed to respond to a few demo cases as explained later ("Experiments", read main())
        '''
        rr_sampling = [0 for x in range(max(dist_fw))]
        rr_sample_2 = [0,0]
        for week in range(num_weeks):
                run_elimination(univ, week)
#UNI_Report        
                for panelist in univ:
                        csv_universe.writerow([experiment, iteration, panelist.indid,str(panelist.rr)[:5],panelist.beta,panelist.recruit,week,numeric_qststatus(panelist),panelist.elimstatus.state])
                complete_interviews = 0
                sample_pull = 1
                daysinfieldwork = random.sample(dist_fw,1)[0]
                daysinfieldworkfixed = daysinfieldwork
                samples_total = []
                samples = []
                while complete_interviews < week_target:
                        eli = eligible(univ)
#ELI_Report
#                        for panelist in eli:
#                                csv_eligible.writerow([experiment, iteration,panelist.indid,week,sample_pull,numeric_qststatus(panelist),panelist.elimstatus.state])
                        if len(eli) == 0: break
                        if rr_sample_2[0] > 0 and rr_sample_2[1] >= 0:
                                if rr_sampling[rr_sample_2[1]]:
#                                OJO!!!: CONVIRTIENDO UN PROBLEMA NUMERICO DE EXPERANZA INFINITA EN UNA PARTICION FRACTIONAL DE TENDENCIA DISCRETA EN LA PROPORCION COMPLETES/SAMPLE_SIZE!!!! (Un problema originado por la variabilidad debida al sample size)
                                        rr_sampling[rr_sample_2[1]] = (rr_sampling[rr_sample_2[1]]+rr_sample_2[0])/2
#                                        rr_sampling[rr_sample_2[1]] = (3*rr_sampling[rr_sample_2[1]]+rr_sample_2[0])/4
                                else:
                                        rr_sampling[rr_sample_2[1]] = rr_sample_2[0]
                        if rr_type == 1: # Using fixed rr universe mean as measure
                                sample = sampling(rr_type, eli, univ, week_target-complete_interviews, rr_calc(univ)/(daysinfieldworkfixed-(daysinfieldwork-1.0)), ir, batches) #target - complete_interviews (count_interviews) = remaining_interviews
                        if rr_type == 2: # Using variable average rr previous sample as measure
                                if rr_sampling[daysinfieldwork-1]:
                                        sample = sampling(rr_type, eli, univ, week_target-complete_interviews, rr_sampling[daysinfieldwork-1], ir, batches)
                                else:
                                        change_rr_type = 1
                                        sample = sampling(change_rr_type, eli, univ, week_target-complete_interviews, rr_calc(univ)/(daysinfieldworkfixed-(daysinfieldwork-1.0)), ir, batches)
                        partial_summary = []
                        count_beta1_uni = 0
                        count_beta2_uni = 0
                        count_beta1_eli = 0
                        count_beta2_eli = 0
                        count_newpan_uni = 0
                        count_oldpan_uni = 0
                        count_newpan_eli = 0
                        count_oldpan_eli = 0
                        legacy_uni = 0
                        nonlegacy_uni = 0
                        legacy_eli = 0
                        nonlegacy_eli = 0
                        for test in univ:
                                if test.beta == 1:
                                        count_beta1_uni += 1
                                else:
                                        count_beta2_uni += 1
                                if test.recruit < week - 12:
                                        count_oldpan_uni += 1
                                else:
                                        count_newpan_uni += 1
                                if test.recruit < -100:
                                        legacy_uni += 1
                                else:
                                        nonlegacy_uni += 1
                        for test in eli:
                                if test.beta == 1:
                                        count_beta1_eli += 1
                                else:
                                        count_beta2_eli += 1
                                if test.recruit < week - 12:
                                        count_oldpan_eli += 1
                                else:
                                        count_newpan_eli += 1
                                if test.recruit < -100:
                                        legacy_eli += 1
                                else:
                                        nonlegacy_eli += 1
                        partial_summary = [experiment, iteration, week, len(univ), str(rr_calc(univ))[:5], str(rr_sample)[:5], str(rr_calc(univ)/(daysinfieldworkfixed-(daysinfieldwork-1.0))*(1-ir))[:5], str(rr_sampling[daysinfieldwork-1])[:5], count_beta1_uni, count_beta2_uni, count_oldpan_uni, count_newpan_uni, legacy_uni, nonlegacy_uni, len(eli), str(rr_calc(eli))[:5], count_beta1_eli, count_beta2_eli, count_oldpan_eli, count_newpan_eli, legacy_eli, nonlegacy_eli, week_target - complete_interviews, len(sample), sample_pull, daysinfieldwork]
#                        everyone in the sample get status Loaded right from the start
                        random.shuffle(sample)
#                        The day_batch wouldn't take the last day of fieldwork of the previous sample, but start all over (in this case, easy if we consider sample_pull)
#                        Additionally there is no currently an implementation for overlapping samples (to be done in the near future)
                        interviews = sample[:]
                        day_batch = 1
                        while day_batch <= daysinfieldwork:
                                if len(interviews) == 0: break
                                if day_batch > daysinfieldwork: break
                                complete_interviews += interviewing_sample(week, sample_pull, day_batch, week_target-complete_interviews, exposure_rate, ir, interviews)
                                day_batch += 1
                                interviews = interviews[:]
                        rr_sample = rr_calc(sample)
                        c, qf, o, b1, b2 = 0, 0, 0, 0, 0
                        new, old, legacy, nonlegacy = 0, 0, 0, 0
                        for test in sample:
#FW_Report and more
                                csv_fieldwork.writerow([experiment, iteration, test.indid, week, sample_pull, test.batch, test_participation(test), numeric_qststatus(test), -77, -77, -77])
#                                csv_fieldwork.writerow([experiment, iteration, test.indid, week, sample_pull, test.batch, test_participation(test), numeric_qststatus(test), test.elimstatus.state, test.participation, test.purged])
                                if test.qstatus == 'C': c += 1
                                if test.qstatus == 'QF': qf += 1
                                if test.qstatus == 'O': o += 1
                                if test.beta == 1:
                                        b1 += 1
                                else:
                                        b2 += 1
                                if test.recruit < week - 12:
                                        old += 1
                                else:
                                        new += 1
                                if test.recruit < -100:
                                        legacy += 1
                                else:
                                        nonlegacy += 1
#                        print(c, qf, o)
#                        print(len(partial_summary))
                        rr_sample_2 = [(c+qf)/len(sample), daysinfieldwork-1]
                        csv_summaries2.writerow([partial_summary[0], partial_summary[1], partial_summary[2], partial_summary[3], partial_summary[4], partial_summary[5], partial_summary[6], partial_summary[7], partial_summary[8], partial_summary[9], partial_summary[10], partial_summary[11], partial_summary[12], partial_summary[13], partial_summary[14], partial_summary[15], partial_summary[16], partial_summary[17], partial_summary[18], partial_summary[19], partial_summary[20], partial_summary[21], partial_summary[22], partial_summary[23], str(rr_sample)[:5], str(rr_sample_2[0])[:5], partial_summary[24], partial_summary[25], c, qf, o, b1, b2, old, new, legacy, nonlegacy])
                        if no_extra: break
                        sample_pull += 1
                        daysinfieldwork = int(daysinfieldwork/2)
                        if daysinfieldwork == 0: daysinfieldwork = 1
#                        Now that exists a notion of DAYS and that there is also extras, what about recruitment and purging on a daily basis?
                purging_f(univ, purged, week)
                new_recruits_f(univ, amount_topurge, week, proportion_beta = pbe)
                max_indid = [univ[-1].indid]                

#
# Following code is to find the exposure rate after a x number of iterations
# The exposure rate is found for a arbitrary ideal sample
# CHECK THE FOLLOWING (wording...): The factor that manage the limit conditions at which the exposure rate is asymptotic is the percentage of quotafuls at the end of the selected fieldwork period

def calc_exposure():
        '''
        # This is a suggested function based on empirical evidence
        # The assumption behind this function is that not all panelists will come to respond the survey just after the invitation (some of them will come later)
        # Therefore it is suggested that there is at least a fixed percentage of remaining sample at any day that will come to answer the questionnarie
        # Probabilistically the response of panelists to an open questionnarie might resemble a Poisson distribution or a bit more complex one
        # Here the use of the nested Bernoullis is again applied
        # Because it is a measuring based on empirical evidence, the procedure involved the definition of an (arbitrary) typical sample
        # There is evidence of the existence of this typical samples in practice as it was later evaluated by other coleagues
        '''
        exposure_rate = 1.0
        avg_exposure_rate = 0
        avg_qf_proportion = 0
        avg_count_qf = 0
        for i in range(1000):
                for exposured in univ:
                        if inspect.ismethod(exposured.qstatus):
                                continue
                        else:
                                exposured.qstatus = None
                                exposured.elimstatus.state = None
                week_target = 35
                complete_interviews = 0
                count_qf = 0
                count_total = 0
                sample_pull = 1
                daysinfieldwork = 4
                ir = 0.15
                while complete_interviews < week_target:
                        if sample_pull > 1: break
                        # IMPORTANT!! My following calculation assumes that the rr_calc(univ) is CORRECT to estimate 1 sample and to get even QF!!!
                        sample = sampling(1, univ, univ, week_target-complete_interviews, rr_calc(univ), ir)
                        interviews = sample[:]
                        day_batch = 1
                        while day_batch <= daysinfieldwork:
                                if len(interviews) == 0: break
                                if day_batch > daysinfieldwork: break
                                complete_interviews += interviewing_sample(week, sample_pull, day_batch, week_target-complete_interviews, exposure_rate, ir, interviews)
                                day_batch += 1
                                interviews = interviews[:]
                        sample_pull += 1
                for interviewed in sample:
                        if interviewed.qstatus == 'QF':
                                count_qf += 1
                        if interviewed.qstatus != 'L':
                                count_total += 1
                if count_total == 0:
                        qf_proportion = 0
                else:
                        qf_proportion = count_qf/count_total
                if qf_proportion > 0.25:
                        exposure_rate -= 0.001
                elif qf_proportion < 0.2:
                        exposure_rate += 0.001
                else:
                        avg_exposure_rate = exposure_rate
                        avg_qf_proportion = qf_proportion
                        avg_count_qf = count_qf
                csv_exposure.writerow([i, str(exposure_rate)[:5], str(qf_proportion)[:5], count_qf])
        file_exposure.close()
        print('\n','--> exposure_rate: ', str(avg_exposure_rate)[:5], 'qf_proportion: ', str(avg_qf_proportion)[:5], 'last count qf: ', avg_count_qf, 'after iteration ', i+1)
        return exposure_rate

        
def main():

        '''
        # The main:
        - collect the desired parameters as entered by the user
        - calculate the parameters required for estimating the composition of the panel corresponding to those desired parameters
        - run a baseline universe
        - calculate an "exposure rate" based on a typical sample
        - run the Experiments
        # The Experiments were designed to run different sampling programs and their effects on efficiencies in sampling
        # Main variables that were evaluated were:
        - The choice of the rr of calculate the sample size (either as given by the current universe or based on remaining eligible
        - The effect of the start days at each sampling effort (weekly) assuming a fixed end date of delivery
        # After this, the effect on size of sampling effort (as number of total samples at the end of the project) and number of
        individuals having a status different to "complete" were analysed and presented
        # Setups are:
        - Experiment1:
        --- sampling within a fixed fieldwork period with extras;
        --- no overlapping of extras (i.e. additional samples until completing the target for that period);
        --- the response rate used to calculate sample size is the response rate of the universe
        - Experiment2:
        --- sampling within a fixed fieldwork period with extras;
        --- no overlapping of extras (i.e. additional samples until completing the target for that period);
        --- the response rate used to calculate sample size is re-estimate of the left eligible after main and extra samples
        - Experiment3:
        --- sampling with different fieldworks periods with a random distribution;
        --- no overlapping of extras (i.e. additional samples until completing the target for that period);
        --- the response rate used to calculate sample size is the response rate of the universe
        - Experiment4:
        --- sampling with different fieldworks periods with a random distribution;
        --- no overlapping of extras (i.e. additional samples until completing the target for that period);
        --- the response rate used to calculate sample size is re-estimate of the left eligible after main and extra samples
        # Results of these experiments were analysed (with R) and presented
        '''
        
        global wished_rr, max_indid, divisor_beta_1, divisor_beta_2, amount_topurge, \
        univ, purged, week
        
        try:
        # Asking the user to decide the desired rr
                while True:
                        wished_rr = input('please input desired rr (0.000 < rr <= 0.280; 0 to terminate): ')
                        weeks = input('please input desired number of weeks of duration of project: ')
                        print('\nWARNING: any estimation of rr will always start at a lower value and (slowly) increase to the desired one at the end of the desired duration (in weeks)', '\n')
                        if float(wished_rr) > 0.0 and float(wished_rr) <= 0.28:
                                print('the given value of rr is '+wished_rr)
                                print('the given value of duration of project in weeks is ', weeks,'\n'*2)
                                wished_rr = float(wished_rr)
                                break
                        elif float(wished_rr) == 0: raise sys.exit()
        except SystemExit:
                        print('leaving')
                        time.sleep(3)
                        sys.exit(0)

        # The following optimisation constraint was arbitrarily included and it is ONLY FOR DEMOSTRATION purposes!!!                
        # (an hyperbolic function makes more sense?... better a polynomial one?...)
        divisor_beta = (wished_rr-0.285)*6/-0.21                                # Arbitrary function based on manual adjustment
        divisor_beta_1 = [divisor_beta+0.5, divisor_beta+0.45]        # Depends on divisor_beta; affect the bad respondents
        divisor_beta_2 = [1.0, 1.15]                                                        # Given as fixed; affect the good respondents
        proportion_beta_est = 0.85                                                                # Starting point
        amount_topurge = 1300                                                                        # Currently fixed value
        max_indid = [-1]                                                                                # Currently NO IDEA why I have to define this here...

        # FUNCTIONS FOR PARAMETER CALCULATIONS: proportion of the bad vs good panelists; exposure_rate
        print('-'*10,'\n'*2)
        print('function parameters_univ() starts now!', '\n')
        # instead of weeks, argument week of the function set to 200 from now on for parameter calculation and baseline
        pbe, arcalc, m = parameters_univ(weeks, proportion_beta_est)
        print('\n')
        print('--> the proportion of beta_1 is {0:.2f}, its rr size divided times {1:.3f}, and ave_rr_calc is {2:.2f}'.format(pbe, abs(m), arcalc))
        print('--> function parameters_univ() was run successfully', '\n'*2, '-'*10, '\n')
        print('function calc_exposure() starts now!', '\n')
        amount_topurge = 1300
        univ = []
        purged = []
        max_indid = [-1]
        week = -200 # OJO: parameter for deciding how many baselines for universes to create
        #print("num_week ",week)
        ##actioning creating universe; set to fixed 200
        creating_baseline_univ(week, pbe, allow_unireport = 1)
        print('a baseline univ has been created for calc_exposure')
        exposure_rate = 0
        exposure_rate = calc_exposure()
        print('--> function calc_exposure() was run successfully', '\n'*2, '-'*10, '\n')
        for i in range(5):
        #        univ = []
        #        purged = []
        #        max_indid = [-1]
        #        week = 0
        #        creating_baseline_univ(week, pbe)
                experiment1 = 1
                experiment2 = 1
                experiment3 = 1
                experiment4 = 1
                exp = [1,2,3,4]
                if experiment1:
        #        Experiment 1: sampling with a fixed fieldwork period; no overlapping of extras; use the overall rr of the universe for calculating the sample size
                        print('a workable baseline_univ() starts now! for exp ',exp[0],' iteration ', i, '\n')
                        amount_topurge = 1300
                        univ = []
                        purged = []
                        max_indid = [-1]
                        week = -200 # OJO: parameter for deciding how many baselines for universes to create
                        creating_baseline_univ(week, pbe)
                        print('\n', '--> a workable baseline_univ was run successfully', '\n'*2, '-'*10, '\n'*2)
                        trackering2(experiment = exp[0], iteration = i+1, num_weeks = int(weeks), week_target = 100, ir = .35, dist_fw = [4])
                
                if experiment2:
        #        Experiment 2: sampling with a fixed fieldwork period; no overlapping of extras; use the rr of the xxxx for calculating the sample size
                        print('a workable baseline_univ() starts now! for exp ',exp[1],' iteration ', i, '\n')
                        amount_topurge = 1300
                        univ = []
                        purged = []
                        max_indid = [-1]
                        week = -200 # OJO: parameter for deciding how many baselines for universes to create
                        creating_baseline_univ(week, pbe)
                        print('\n', '--> a workable baseline_univ was run successfully', '\n'*2, '-'*10, '\n'*2)
                        trackering2(experiment = exp[1], iteration = i+1, num_weeks = int(weeks), week_target = 100, ir = .35, dist_fw = [4], rr_type = 2)

                if experiment3:
        #        Experiment 3: sampling with different fieldworks periods with a random distribution; no overlapping of extras
                        print('a workable baseline_univ() starts now! for exp ',exp[2],' iteration ', i, '\n')
                        amount_topurge = 1300
                        univ = []
                        purged = []
                        max_indid = [-1]
                        week = -200 # OJO: parameter for deciding how many baselines for universes to create
                        creating_baseline_univ(week, pbe)
                        print('\n', '--> a workable baseline_univ was run successfully', '\n'*2, '-'*10, '\n'*2)
                        trackering2(experiment = exp[2], iteration = i+1, num_weeks = int(weeks), week_target = 100, ir = .35, dist_fw = [4,4,4,4,4,4,3,3,3,3,2,2,1])
        
                if experiment4:
        #        Experiment 4: sampling with different fieldworks periods with a random distribution; no overlapping of extras
                        print('a workable baseline_univ() starts now! for exp ',exp[3],' iteration ', i, '\n')
                        amount_topurge = 1300
                        univ = []
                        purged = []
                        max_indid = [-1]
                        week = -200 # OJO: parameter for deciding how many baselines for universes to create
                        creating_baseline_univ(week, pbe)
                        print('\n', '--> a workable baseline_univ was run successfully', '\n'*2, '-'*10, '\n'*2)
                        trackering2(experiment = exp[3], iteration = i+1, num_weeks = int(weeks), week_target = 100, ir = .35, dist_fw = [4,4,4,4,4,4,3,3,3,3,2,2,1], rr_type = 2)

        file_universe.close()
        file_eligible.close()
        file_fieldwork.close()
        file_summaries.close()
        file_summaries2.close()



if __name__ == "__main__":
        main()

