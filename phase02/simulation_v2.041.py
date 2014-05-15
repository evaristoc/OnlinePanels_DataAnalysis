import sys, os
import random, math
from collections import namedtuple, defaultdict
import inspect
import csv
import itertools
import operator
import copy
import inspect
import cProfile

# TODO:
# - Start solving Panelist so he can keep a list of the projects he has finished
# - Perhaps adding additional lists to save statuses in other classes? Perhaps one important one is week
# ----- I am creating a sort of DATABASE through dictionary in class instances, so try to be organised...
# - Prepare the completion model and how to access it
# ----- This includes the threading process!!! So get it ready...
# - Prepare the universe creation model (RELEVANT!)

class counter(object):
        '''
        # A simple counter based on a closure structure
        # It would be relevant at different stages for different methods of all classes
        # E.g. at the sampling section when imposing elimination rules (period of not allowed sampling)
        '''
        def __init__(self, start):
                self.state = start
        def __call__(self, week):
                if self.state:
                        self.state -= 1
                if self.state == 0:
                        self.state = None

class Panelist(object):
        '''
        # Definition of attributes of a "panelist"
        # Attributes are defined in terms of response and panel life cycle characterisation
        # Additional attributes could be added
        '''
        superweek = 0
        
        def active_tenure(self, kappa_scale = 0.73, lambda_shape = 0.44):
                '''
                Survival in weeks
                - Using R data:
                --- 1/kappa: scale parameter alpha in Python (kappa = 0.73)
                --- lambda: shape parameter beta in Python (lambda = 0.44)
                '''
                self.act_ten = 1
                self.act_ten += round(random.weibullvariate(1/kappa_scale,lambda_shape))
                #return self.act_ten 
        getacttenure = property(active_tenure, doc = 'assigned act tenure as weibull random variate')

        def __init__(self, indid = -1, week = -1):
                self.indid = indid
                self.startweek = week
                self.getacttenure
                self.touchedsurvs = [('survid','week','touchstatus (1=complete, 2=other)')]
                self.status = True
                self.inact_period = random.random()
                self.startinactten = -1
                self.startpurge = -1
        def rr_func(self, kf_a1 = -0.079,  kf_a2 = 1.5e-3, kf_b = 1.70, mhuf_a = 0.014, mhuf_b = 0.54):
                '''
                The function associated to the assigned lifetime
                - Using R data and corresponding active tenure after assignment:
                --- kf_a1, kf_a2, kf_b: the coefficients of the k parameter of the corresponding neg-bin
                                        (kf_a1 = -0.079, kf_a2 = 0.0015, kf_b = 1.70)
                --- mhuf_a, mhuf_b: the coefficients of the alpha parameter of the corresponding neg-bin
                                        (mhuf_a = 0.014, mhuf_b = 0.54)
                '''
                negbin_par = namedtuple("negbin_par", ('k', 'mhu'))
                self.k = kf_a1*self.act_ten + kf_a2*self.act_ten**2 + kf_b
                log_mhu = mhuf_b + mhuf_a*self.act_ten
                self.mhu = math.exp(log_mhu)
                negbinp = negbin_par(self.k,self.mhu)
                return negbinp
        getrr = property(rr_func, doc = 'parameters of neg bin function based on active tenure and empirical behaviour')
        def cumnegbin(self, s, p, n):
                '''
                For the first demo I will use the cum dist of the negbin as in:
                #http://stackoverflow.com/questions/1095650/how-can-i-efficiently-calculate-the-binomial-cumulative-distribution-function
                see also:
                http://docs.scipy.org/doc/numpy/reference/generated/numpy.random.negative_binomial.html
                '''
                x = 1.0 - p
                a = n - s
                b = s + 1
                c = a + b - 1
                prob = 0.0
                for j in range(a, c + 1):
                        prob += math.factorial(c) / (math.factorial(j)*math.factorial(c-j)) * x**j * (1 - x)**(c-j)
                return prob
        def touch_func(self, num_surs):
                '''
                The model takes the cumnegbin dist and use an accept/reget method compared to a uniform random variable
                by calculating succesive values along the cumnegbin until the dist is higher or equal to
                the uniform random variable
                The negbin model and the method above has been tested with data from field and coincides with empirical observations
                but still could incorrectly stop too early when reaching the asymptotic level of
                the cumulative curve (P=1.0 or P=0.0, depending...)
                The following will be taken in account for the touch model:
                - The assumption is that the more the invites to an active panelist,
                  the higher the chance of touching at least once
                  This works well with the cumnegbin dist assumption; I will use a binomial to accept/reget method
                --- The assumption has showed to be valid under certain conditions but NOT ALWAYS so this is a partial result
                - For the moment the model ignores aspects like:
                --- invitiation quality
                --- survey quality
                --- effect of past experience; professionalism
                '''
                comparing_val = random.uniform(0,1)
                p = self.getrr.k/(self.getrr.k+self.getrr.mhu)
                num_touch = 0
                if comparing_val >= self.cumnegbin(0, p, num_surs):
                        num_touch += 1
                        for ns in range(1,num_surs+1):
                                if comparing_val > (self.cumnegbin(ns,p,num_surs)-self.cumnegbin(ns-1,p,num_surs))/(self.cumnegbin(num_surs,p,num_surs)-self.cumnegbin(ns-1,p,num_surs)):
                                        num_touch += 1
                                else:
                                        break
                return num_touch
        def weekly_touched_surveys(self, week, updated_portal):
                '''
                - touch status complete = 1; other touch status = 2
                '''
                if self.status == True:
                        num_surs = len(updated_portal)
                        num_touch = self.touch_func(num_surs)
                        if num_touch > 0:
                                for s in range(num_touch):
                                        if updated_portal[s].exp_incidence >= random.random():
                                                self.touchedsurvs.append((updated_portal[s].survid, week, 1))
                                                updated_portal[s].ch_completes(1)
                                        else:
                                                self.touchedsurvs.append((updated_portal[s].survid, week, 2))
        def inactive_tenure(self):
                '''
                Applying the model for dead tenure
                self.status = False is for dead
                '''
                
                if Panelist.superweek - self.startweek == self.act_ten:
                        self.status = False
                        self.startinactten = Panelist.superweek
        setinactten = property(inactive_tenure)
        def purged(self):
                '''
                Making the purging based on dead tenure
                self.status = None is for purged
                '''
                if self.status == False and ((Panelist.superweek - self.startinactten == 5 and self.inact_period <= .5) or (Panelist.superweek - self.startinactten == 18 and self.inact_period >= .5)):
                        self.status = None
                        self.startpurge = Panelist.superweek
        setpurged = property(purged)
        def recruit (self, recruit = None):
                self.recruit = recruit
        def pstatus(self, pstatus = None):
                self.pstatus = pstatus
        def elimstatus(self, elimstatus):
                self.elimstatus = elimstatus
        def participation(self, participation = {}):
                self.participation = participation
        def batch(self, batch):
                self.batch = -77
        def visit_rr(self, p = None):
                '''
                Should be a random variable based on active tenure and rr
                '''
                pass
        def qstatus(self, qstatus = None):
                '''
                The last touching status variable
                Should be reinitiated after leaving the portal
                '''
                self.qstatus = qstatus

class survey_study(object):
        '''
        This class will initiate a survey study, defining its specs and current completion status
        Each survey has an id, surid 
        The survey closes either when the completes are reached or at end of specified fieldwork
        Use the counter to track status
        Could eventually include a difference between trackers and ad-hocs
        /// OJO: Previous included an expiration date but the most recent one will be just instantaneous! ///
        '''
        def __init__(self, survid, start_week, exp_completes = 100, exp_incidence = .20, exp_fw = 1, status = True):
                '''
                originally the initial settings were:
                survid = 0, exp_completes = 100, exp_incidence = .20, exp_fw = 4, status = True
                I changed exp_fw for = 1...
                '''
                self.survid = survid
                # start_week: temporary solution to completing update
                self.start_week = start_week
                self.exp_fw = exp_fw
                self.ch_completes = counter(exp_completes)
                self.ch_fw = counter(self.exp_fw)
                self.exp_completes = exp_completes
                self.exp_incidence = exp_incidence
                self.status = status
        def completing(self, current_week):
                '''
                Completing is occurring at Panelist! Panelist will save the information about this aspect
                For this method I will only update the status of the survey for the moment...
                '''
                if current_week > self.start_week:
                        self.ch_fw(current_week)
                if self.ch_completes.state == None or self.ch_fw.state == None:
                        self.status = False

class full_inbox(survey_study):
        '''
        Think not need to be a class but a global variable
        The full_inbox includes all the surveys in a unique list
        New surveys would be added randomly and weekly
        The idea is to also retire those surveys that are filled or reached the time
        '''
        def __init__(self):
                self.survey_studies = []
        def add_studies(self, new_stu):
                '''
                check this... maybe not needed...
                '''
                for i in new_stu:
                        if i.status:
                                if i not in self.survey_studies:
                                        self.survey_studies.append(i)
                return self.survey_studies
        def update_week_studies(self, current_week):
                if self.survey_studies:
                        for ss in self.survey_studies:
                                ss.completing(current_week)        
        def active_studies(self):
                '''
                find the first True (active) in the list and report the value...
                it should be ACTINBOX + the new surveys!!!! Otherwise I will be making longer this list!!!
                '''
                sort_active = self.survey_studies[:]
                sort_active.sort(key=lambda stu: stu.status)
                try:
                        self.actinbox = copy.copy(sort_active[next((index for index, active in enumerate(sort_active) if active.status==True)):])
                except StopIteration:
                        self.actinbox = []
                return self.actinbox
        p_actinbox = property(active_studies)

class portal(full_inbox, Panelist):
        '''
        This class should be a SUBCLASS of INBOX! (OK)
        This sub-class is meant to represent all available surveys to the panelist
        If the survey is filled or it is unavailable it shouldn't be in the portal
        The panelist participate only on those surveys that are in the portal
        '''
        def __init__(self, portalid, inbox):
                self.portalid = portalid
                self.myinbox = inbox.p_actinbox
        def up_view_myinbox (self, p):
                if p.touchedsurvs:
                        current_act = next((index for index,(a,wk,b) in enumerate(p.touchedsurvs[1:]) if wk>=week-8), None)
                        if current_act:
                                for touchedsurvid, touchedsurvwk, touchedstatus in p.touchedsurvs[current_act:]:
                                        for activesurv in self.myinbox:
                                                if touchedsurvid == activesurv.survid:
                                                        self.myinbox.remove(activesurv)
                return self.myinbox

def universe():
        '''
        For universe:
        - Start with an empty list of purged people and a group of recruits
        - If a week pasts, update the full universe
        - Now reorder from status False to True and do the following:
        --- Find the next False and while False, verify if purging is apropriate
        --- Those with status None should be dumped in purged list
        --- Now find status True and make them False if apropriate
        - Create a fix number of recruitments per week and add them to the universe
        - Count the following week
        Because not using numpy this is not vectorizable...
        '''
        pass

def wk_studies():
        '''
        number of studies per wk
        - Always have 1 or 2 per week
        - the rest is selected using a sampling for a binomial (see Givens & Hoeting) for:
        --- 30 trials
        --- p = 0.2
        '''
        pass


def sampling():
        '''
        Here I will implement a sampling scheme (still don't know if by periods and replacement with a yield?)
        and a threading to take care of the sampling of the existing universe
        The functionality could be as following:
        - Make the sample according to panelists rr's, a wet thumb rule based on empirical observations or take the full universe
        - Start threading lock
        - Individually update weekly portals
        - Calculate touches
        - Update survey statuses and week values
        --- If survey became False, continue without updating
        - Open threading lock
        Sampling occurs after every universe update
        '''
        pass


def test_process():
        def study_wk_test(ss, current_week):
                added_wk = len(ss)
                for i in range(1,4):
                        ss.append(survey_study(i+added_wk, current_week, exp_completes = 5, exp_fw = 1))
                        #for l in ss:
                        #        print(l.start_week)
                return ss
        #uni_test = [Panelist(i,0) for i in range(1,11)]
        recruits = [Panelist(i,0) for i in range(1,11)]
        for p in recruits:
                p.rr_func()
        uni_test = recruits[:]
        print(uni_test[0].__dict__)
        #uni_test[0].inactive_tenure(uni_test_wk00[0].getacttenure)
        ss = []
        inbox = full_inbox()
        #ss = study_wk_test(ss, 0)
        #inbox.add_studies(ss)
        for week in range(1,11):
                # studies per week
                ss = study_wk_test(ss, week-1)
                inbox.add_studies(ss)
                #entryinbox = inbox.p_actinbox
                print(len(ss))
                # sampling
                for p in uni_test:
                        pportal = portal(p.indid, inbox)
                        p.weekly_touched_surveys(week-1, pportal.up_view_myinbox(p))
                # weekly survey status update
                inbox.update_week_studies(week)
                print(len(inbox.survey_studies))
                print(len(inbox.p_actinbox))
                # panelist status update
                Panelist.superweek = week
                new_round = len(uni_test)
                for p in uni_test:
                        if p.status == None:
                                continue
                        elif p.status == False:
                                p.setpurged
                        elif p.status == True:
                                p.setinactten
                recruits = [Panelist(i+new_round,week) for i in range(1,11)]
                uni_test = uni_test+recruits
        return inbox, uni_test


#cProfile.run('test_process()')
inbox, uni_test = test_process()
