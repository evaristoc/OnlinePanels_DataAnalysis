import sys, os
import random, math
from collections import namedtuple, defaultdict
import inspect
import csv
import itertools
import operator
import copy
import inspect

#max_indid = [-1]
#divisor_beta_1 = [-1,-1]
#divisor_beta_2 = [-1,-1]
#amount_topurge = -1
#wished_rr = .28
#univ = [None]
#purged = [None]
#week = 0
#exposure_rate = 0
#pbe = 0

# TODO:
# - Start solving Panelist so he can keep a list of the projects he has finished
# - Perhaps adding additional lists to save statuses in other classes? Perhaps one important one is week
# ----- I am creating a sort of DATABASE through dictionary in class instances, so try to be organised...
# - Prepare the completion model and how to access it
# ----- This includes the threading process!!! So get it ready...
# - Prepare the universe creation model (RELEVANT!)
# OJO: https://docs.python.org/3/library/functions.html#property
# http://stackoverflow.com/questions/16025462/what-is-the-right-way-to-put-a-docstring-on-python-property


class counter(object):
        '''
        # A simple counter based on a closure structure
        # It would be relevant at different stages for different methods of all classes
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



class Panelist(object):
        '''
        # Definition of attributes of a "panelist"
        # Attributes are defined in terms of response and panel life cycle characterisation
        # Additional attributes could be added
        '''
        def active_tenure(self, kappa_scale = 0.73, lambda_shape = 0.44):
                '''
                Survival in weeks
                - Using R data:
                --- 1/kappa: scale parameter alpha in Python (kappa = 0.73)
                --- lambda: shape parameter beta in Python (lambda = 0.44)
                '''
                self.act_ten = int(random.weibullvariate(1/kappa_scale,lambda_shape))
                return self.act_ten   
        getacttenure = property(active_tenure, doc = 'assigned act tenure as weibull random variate')
        def __init__(self, indid = -1):
                self.indid = indid
                self.getacttenure
                self.touchedsurvs = []
                self.status = True
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
        def cumnegbin(s, p, n):
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
        def touch_func(num_surs):
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
                p = self.k/(self.k+self.mhu)
                num_touch = 0
                if comparing_val >= cumnegbin(0, p, num_surs):
                        num_touch += 1
                        for ns in range(1,num_surs+1):
                                if comparing_val > (cumnegbin(ns,p,num_surs)-cumnegbin(ns-1,p,num_surs))/(cumnegbin(num_surs,p,num_surs)-cumnegbin(ns-1,p,num_surs)):
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
                        num_touch = touch_func(num_surs)
                        if num_touch > 0:
                                for s in range(num_touch):
                                        if updated_portal[s].exp_incidence >= random.random():
                                                self.touchedsurvs.append((updated_portal[s].survid, week, 1))
                                                updated_portal[s].ch_completes(1)
                                        else:
                                                self.touchedsurvs.append((updated_portal[s].survid, week, 2))
                return self.touchedsurvs
        def dead_tenure(self):
                '''
                Applying the model for dead tenure
                self.status = False is for dead
                '''
                self.status = False
        def purged(self, purged = None):
                '''
                Making the purging based on dead tenure
                self.status = None is for purged
                '''
                self.status = None
                #self.purged = purged
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




class survey_study(object):
        '''
        This class will initiate a survey study, defining its specs and current completion status
        Each survey has an id, surid 
        The survey closes either when the completes are reached or at end of specified fieldwork
        Use the counter to track status
        Could eventually include a difference between trackers and ad-hocs
        /// OJO: Previous included an expiration date but the most recent one will be just instantaneous! ///
        '''
        def __init__(self, survid = 0, exp_completes = 100, exp_incidence = .20, exp_fw = 4, status = True):
                self.survid = survid
                self.ch_completes = counter(exp_completes)
                self.ch_fw = counter(exp_fw)
                self.exp_completes = exp_completes
                self.exp_incidence = exp_incidence
                self.status = status
        def completing(self, Panelist, specs):
                '''
                /// CHECK!!! THIS WILL CHANGE AS THE UPDATE WILL BE MADE AT PANELIST CLASS!!
                    ALSO, qstatus WILL NOT BE MORE A STATUS FORMAT FOR THIS PROJECT, only 1 or 2
                '''
                if Panelist.qstatus() != 'L':
                        specs(self).exp_completes(Panelist.qstatus)
                if week:
                        specs(self).exp_fw(week)
                if specs(self).exp_completes() == 0 or specs(self).exp_fw() == 0:
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
        def active_studies(self):
                '''
                find the first True (active) in the list and report the value...
                '''
                #http://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-in-python-based-on-an-attribute-of-the-objects
                #OJO: it is an IN-PLACE form of sorting!!!, so cannot be assigned!!!
                sort_active = self.survey_studies[:]
                sort_active.sort(key=lambda stu: stu.status)
                # eventually a try-except here: active surveys could be exhausted at a point!!!
                self.actinbox = copy.copy(sort_active[next((index for index, active in enumerate(sort_active) if active.status==True), None):])
                return self.actinbox
        #def exclude(self, survey_study):
        #        if survey_study.completing.status() == False:
        #                self.survey_studies.remove(survey_study)
        p_actinbox = property(active_studies)

class portal(full_inbox):
        '''
        This class should be a SUBCLASS of INBOX! (OK)
        This sub-class is meant to represent all available surveys to the panelist
        If the survey is filled or it is unavailable it shouldn't be in the portal
        The panelist participate only on those surveys that are in the portal
        '''
        def __init__(self, portalid, myinbox):
                self.portalid = portalid
                self.myinbox = myinbox.p_actinbox[:]
        def up_myinbox (self, myinbox):
                #self.myinbox = self.act_inbox[:]
                if Panelist.touchedsurvs:
                        current_act = next((index for index, (stat, wk) in enumerate(f_surs) if wk>=week-8), None)
                        if current_act:
                                for touchedsurvid, touchedsurvwk in Panelist.touchedsurvs[current_act:]:
                                        for activesurv in self.myinbox:
                                                if touchedsurvid == activesurv.survid:
                                                        self.myinbox.remove(activesurv)
                return self.myinbox



# p1 = Panelist(1)
### OBS:
### With the current setting at active_tenure and rr which are not set as properties and don't have
### a return, the only way to initialise the attributes associated to them is by an unbound calling
### of the modules:
##### p1.active_tenure()
##### p1.rr()
### So I changed the order of active_tenure to become a property assigned to __init__ without calling
### and make getrr a property so it calculates the values at calling
# p1.getrr
# ss1 = survey_study(1)
# ss2 = survey_study(2)
# ss3 = survey_study(3)
# NO total_inbox = full_inbox([ss1, ss2, ss3])
# total_inbox = full_inbox()
# total_inbox.add_studies([ss1, ss2, ss3])
# total_inbox.p_actinbox
# full_inbox.__dict__
# mi1 = portal(p1)
# ss1.status = False
# p1.filled_surveys = [(1,'C'), (2,'C')] #temporary
# panelists = []
# for i in range(100):
#       panelists.append(Panelist(i))
# surveys = []
# for i in range(10):
#       surveys.append(survey_study(i))
# total_inbox.add_studies(surveys)


def universe():
        pass

def purging():
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
        pass

