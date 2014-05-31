#exec(open('/media/evaristo/KINGSTON/Project_SIM/simulation/phase02/simulation_v2.10.py').read())

import sys, os
import random, math
from collections import namedtuple
import time
import multiprocessing

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

        def active_tenure(self, *surv_parm):
                '''
                Survival in weeks
                - Updating the parameters of a proposed survival function to get act_ten
                '''
                self.act_ten = 1
                self.act_ten += random_func_surv(surv_parm)
        
        def __init__(self, indid = -1, week = -1, *attr_par):
                self.indid = indid
                self.startweek = week
                self.act_ten = act_ten()
                self.touchedsurvs = [('survid','week','touchstatus (1=complete, 2=other)')]
                self.status = 1 #True
        def rr_func(self):
                '''
                we get the parameters of the random function for rr based on a function that links
                rr to active tenure
                '''
                self.par_rr = func_par_rr(act_ten)
        def inactive_tenure(self):
                '''
                Applying the model for inactive tenure
                self.status = 0 is for inactive
                '''
                updateinactive = random_func_inactive(week, act_ten)
                if updateinactive:
                        self.status = 0
        def purged(self):
                '''
                Making the purging based on dead tenure
                self.status = -1 is for purged
                '''
                updatepurge = random_func_purge(week, self.status)
                if updatepurge:
                        self.status = -1
        def weekly_touched_surveys(self, portal):
                '''
                based on the number of surveys available we calculate the number of
                surveys that would be touched by the panelist before failure
                and transform the value into a random variable
                Then we update the values of the surveys in portal
                '''
                num_surv = len(portal)
                self.numtouch = transf_func_rr(cum_func_rr(par_rr, num_surv))
                for ind, u in enumerate(num_surv):
                        update_function(portal[ind])

class Survey_Study(object):
        '''
        This class will initiate a survey study, defining its specs and current completion status
        Each survey has an id, surid 
        The survey closes either when the completes are reached or at end of specified fieldwork
        Use the counter to track status
        Could eventually include a difference between trackers and ad-hocs
        '''
        def __init__(self, survid, start_week, *specs):
                '''
                initial settings
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
        def completing(self, week):
                '''
                Completing is occurring at Panelist! Panelist will save the information about this aspect
                For this method I will only update the status of the survey for the moment...
                '''
                if week > self.start_week:
                        self.ch_fw(week)
                if self.ch_completes.state == None or self.ch_fw.state == None:
                        self.status = False

class Full_Inbox(Survey_Study):
        '''
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

class portal(Full_Inbox, Panelist):
        '''
        This sub-class is meant to represent all available surveys to the panelist
        If the survey is filled or it is unavailable it shouldn't be in the portal
        The panelist instance "participates" only on those surveys instances that are available in
        the panelist instance's portal
        '''
        def __init__(self, portalid, inbox):
                self.portalid = portalid
                self.myinbox = inbox.p_actinbox
        def up_view_myinbox (self, p, week):
                if p.touchedsurvs:
                        current_act = next((index for index,(i,wk,d,s) in enumerate(p.touchedsurvs[1:]) if wk>=week-8), None)
                        if current_act:
                                for touchedsurvid, touchedsurvwk, touchedsurvday, touchedstatus in p.touchedsurvs[current_act:]:
                                        for activesurv in self.myinbox:
                                                if touchedsurvid == activesurv.survid:
                                                        self.myinbox.remove(activesurv)
                return self.myinbox        


def universe(uni = [], purged = [], week = 0):
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
        I am not using numpy for this one...
        '''
        if uni:
                Panelist.superweek = week
                for p in uni:
                        if p.status == -1:
                                continue
                        elif p.status == 0:
                                p.purged()
                        elif p.status == 1:
                                p.inactive_tenure()
        uni.sort(key=lambda stu: stu.status)
        try:
                indexes = [i for i,p in enumerate(uni) if p.status == -1]
                for i in indexes:
                        purged.append(uni[i])
                        uni.remove(uni[i])
        except:
                purged = purged + []
        recruits = [Panelist(i+len(uni)+len(purged),week) for i in range(1,int(4000/3))]
        for p in recruits:
                p.rr_func()
        uni = uni + recruits[:]
        return uni, purged

# baseline_uni becomes a worker
def baseline_uni(arg, q):
        uni,purged = universe([],[])
        record = [0, 0, 0, len(uni), len(purged)]
        for wk in range(1, wks_52*years+1): #2 years of "baseline"
                uni, purged = universe(uni,purged,wk)
        return len(uni), len(purged)

def sampling(uni,purged):
        ss = []
        inbox = full_inbox()
        for endofweek in range(wks_52*years+1,wks_52*(years+1)+1): #starts next week of year 3 and advances up to the end of year 3
                record = []
                startofweek = endofweek-1
                ss = wk_studies(ss, startofweek)
                inbox.add_studies(ss)
                active_completion(uni, inbox, startofweek)
                inbox.update_week_studies(endofweek)
                uni, purged = universe(uni, purged, endofweek)
        return inbox, uni, purged


