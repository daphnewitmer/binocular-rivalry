from exptools.core.trial import Trial
import os
import exptools
import json
from psychopy import logging, visual, event, clock, core
import numpy as np
from scipy.ndimage.filters import gaussian_filter
import scipy as sp
from scipy import stats
import pandas as pd
import random


class MEG_BR_Trial(Trial):
   
    # Define the display framework upon which stimulus is presented
    def __init__(self, ti, run_type, duration, color_eye_combination, config, parameters, *args, **kwargs):
        self.color = '#0066CC'
        self.previous_frame = 0
        self.val= 0
        
        self.run_type = run_type
        self.ID = ti
        self.repeat = 0
        self.trigger = 999
        self.duration= duration
        self.p = False

        phase_durations = [100000,
                           config['fixation_duration'],
                           self.duration, 
                           config['fixation_duration'],
                           config['count_duration']
                           ]

        super(
            MEG_BR_Trial,
            self).__init__(
            phase_durations=phase_durations,
            parameters=parameters,
            *args,
            **kwargs)

        self.parameters.update(config)
        self.create_stimuli()
        
        # initialize variables
        self.timing_array = []
        self.frame = 0

        self.red_flicker_frame, self.green_flicker_frame = 0, 0
        self.red_orientation, self.green_orientation = 0, 0

        safety_margin = 10.0
        nr_frames_in_stimulus = int(
            (self.duration + safety_margin) * self.parameters['refresh_frequency'])
        frame_times = np.linspace(
            0, self.duration + safety_margin, nr_frames_in_stimulus, endpoint=False)

        if parameters['replay'] == 1:
        
            beh_id = [random.choice([1,3])] #1,3 correspond to button press
            beh_time = [random.normalvariate(2,0.25)]
            while beh_time[-1] < self.duration:
                if beh_id[-1] == 3:
                    beh_id.append(1) 
                else:
                    beh_id.append(3)    
                flip = random.normalvariate(2,0.5)
                beh_time.append(beh_time[-1]+flip) 
            
            self.behavior_df = pd.DataFrame([beh_id, beh_time])
            self.behavior_df = self.behavior_df.transpose()
            self.behavior_df.columns = ['ID', 'Time']

            rp_percept_per_frame = np.ones(nr_frames_in_stimulus) * 2
            time_per_frame = np.arange(0, nr_frames_in_stimulus/float(
                self.parameters['refresh_frequency']), 1/float(self.parameters['refresh_frequency']))
            for percept, time in zip(self.behavior_df['ID'], self.behavior_df['Time']):
                rp_percept_per_frame[time_per_frame > time] = (percept-1)/2.0

            # the number multiplied by refresh frequency specifies the 'duration' of the
            # transition between states. Make it 0, and they're instantaneous.
            smoothed_rp_percept_per_frame = gaussian_filter(
                rp_percept_per_frame, 0 * self.parameters['refresh_frequency'])

            self.rg_opacity_indices = np.array([smoothed_rp_percept_per_frame, 1-smoothed_rp_percept_per_frame]) * np.array([
                1, self.parameters['BR_stim_RG_ratio']])[:, np.newaxis]
                
#            self.rg_opacity_indices = np.ones((2, nr_frames_in_stimulus)) * np.array(
#                [1, self.parameters['BR_stim_RG_ratio']])[:, np.newaxis]
        else:
            self.rg_opacity_indices = np.ones((2, nr_frames_in_stimulus)) * np.array(
                [1, self.parameters['BR_stim_RG_ratio']])[:, np.newaxis]

        self.rg_opacity_indices = np.clip(self.rg_opacity_indices, 0, 1)

        self.parameters['percept_count'] = np.random.choice([5, 6, 7, 8])
        
    def create_stimuli(self):
        """ initialize instruction text """

        this_instruction_string = "\n\nPlease keep fixation on the dot"

        if self.ID == 0:
            this_instruction_string = this_instruction_string.replace(
                "Press any key to start", "Trial will begin soon")

        self.instruction_left = visual.TextStim(self.screen,
                                                text=this_instruction_string,
                                                font='Helvetica Neue',
                                                pos=self.session.left_pos,
                                                italic=True,
                                                height=20,
                                                alignText='center',
                                                color=(1, 0, 0))
        self.instruction_right = visual.TextStim(self.screen,
                                                 text=this_instruction_string,
                                                 font='Helvetica Neue',
                                                 pos=self.session.right_pos,
                                                 italic=True,
                                                 height=20,
                                                 alignText='center',
                                                 color=(1, 0, 0))

    def draw(self, *args, **kwargs):
        """ draw stimli that where initialized in session.py """
        
        # draw background and fixation dots
        self.session.bg_stimulus_left.draw()
        self.session.bg_stimulus_right.draw()
        self.session.grating_bg_left.draw()
        self.session.grating_bg_right.draw()
        self.session.fixation_left.draw()
        self.session.fixation_right.draw()
        
        # before starting the experiment (phase 0) draw instructions
        if (self.phase == 0):
            self.instruction_left.draw()
            self.instruction_right.draw()
            
        # draw stimuli in stimulus presentation phase
        if self.phase == 2:  
            pres_time = clock.getTime() 
            time_since_phase = pres_time - self.last_phase_time
            
            # measure the number of frames that have passed 
            frame_since_phase = int(time_since_phase * self.parameters['refresh_frequency'])
            self.frame = frame_since_phase # current frame number 
            
            # Stim Flicker Frequency; Also check: https://stackoverflow.com/questions/37469796/where-can-i-find-flickering-functions-for-stimuli-on-psychopy-and-how-do-i-use
            # color_flicker_frequency_contingency is set to 1 in session.py
            # In Python: [16,12][1] = 12; hence, if color_flicker_frequency_contingency=1, the second value out of the two is chosen
            red_ff = [self.parameters['high_flicker_period_frames'], 
            self.parameters['low_flicker_period_frames']][self.parameters['color_flicker_frequency_contingency']] 
                      
            # In Python: [16,12][0] = 16; hence, if [1 - color_flicker_frequency_contingency]=0, the first value out of the two is chosen
            # Also, in the default_Settings.json file, make sure the following values are set for a monitor refresh rate of 240Hz:
            #	"high_flicker_period_frames": 8,	"low_flicker_period_frames": 10,
            # This will ensure the left stimulus flickers at 12 Hz and the right at 15 Hz
            green_ff = [self.parameters['high_flicker_period_frames'], self.parameters['low_flicker_period_frames']
                        ][1-self.parameters['color_flicker_frequency_contingency']]
                        
            flicker_level_red = int(np.floor(self.frame % (red_ff*2) / red_ff))
            flicker_level_green = int(np.floor(self.frame % (green_ff*2) / green_ff))
                

            # I assume the following couple of lines use an older method to calculate flicker level
            # flicker_level_red = int((self.frame%red_ff)==0) # changing the value of the 
            # flicker_level_green = int((self.frame%green_ff)==0)
            # Commenting out the next 5 lines doesnt seem to have much effect
            if flicker_level_green != self.green_flicker_frame and flicker_level_green == 1:
                self.green_orientation = self.parameters['grating_rotation_speed'] * \
                    pres_time*self.parameters['motion_direction'] * 360.0
            if flicker_level_green != self.green_flicker_frame:
                self.green_flicker_frame = flicker_level_green

            if flicker_level_red != self.red_flicker_frame and flicker_level_red == 1:
                self.red_orientation = self.parameters['grating_rotation_speed'] * \
                    pres_time * \
                    self.parameters['motion_direction'] * 360.0  # + 90.0 # I uncommented + 90.0 but that didn't have much effect
            if flicker_level_red != self.red_flicker_frame:
                self.red_flicker_frame = flicker_level_red

            present_red_grating = [self.session.red_grating_1,
                                   self.session.red_grating_2][flicker_level_red]
            present_green_grating = [
                self.session.green_grating_1, self.session.green_grating_2][flicker_level_green]

            present_red_grating.setOri(self.red_orientation)
            present_green_grating.setOri(self.green_orientation)

            present_red_grating.setOpacity(
                self.rg_opacity_indices[0, self.frame])
            present_green_grating.setOpacity(
                self.rg_opacity_indices[1, self.frame])

            # if flicker_level_red == 0:
            #     present_red_grating.setOpacity(0)
            # if flicker_level_red == 1:
            #     present_red_grating.setOpacity(self.rg_opacity_indices[0,self.frame])
            # if flicker_level_green == 0:
            #     present_green_grating.setOpacity(0)
            # if flicker_level_green == 1:
            #     present_green_grating.setOpacity(self.rg_opacity_indices[1,self.frame])
            
            ## set the rotation angles based on time_since_phase
#            present_red_grating.setOri(time_since_phase*360)
#            present_green_grating.setOri(time_since_phase*-100)
            present_red_grating.radialPhase = time_since_phase
#            present_green_grating.angularPhase = time_since_phase

            # present colored stimuli
            present_red_grating.draw()
            present_green_grating.draw()
            self.session.fixation_surround_left.draw()
            self.session.fixation_surround_right.draw()
            
            # for localizer fixation task: change fixation dot color
            if "fix" in self.run_type:
                event_nr = int(4) # change fixation dot color to blue
                if self.previous_frame + self.val <= self.frame:
                    if self.color == '#0066CC':
                        self.color = "white"  
                        self.val = random.randint(1600, 2400)
                    else:
                        self.color= '#0066CC'
                        self.val = 80
                        self.session.port.setData(event_nr)
                        core.wait(0.005)
#                        self.p = True
#                        print('-------trigger fix---------')
#                        print(clock.getTime())
                        self.timing_array.append(
                                [int(event_nr), clock.getTime() - self.last_phase_time])
                        
                    self.session.port.setData(0)
                    self.previous_frame = self.frame
                    self.session.fixation_left.color = self.color
                    self.session.fixation_right.color = self.color
                    
            # add triggers for red-green switch localizer
            if 'loc' in self.run_type.lower():
                red=1
                green=3
                
                if self.session.config['use_parallel'] == 1:
                    if present_green_grating.opacity == 0:
                        if self.trigger is not red:
                            self.trigger = red
                            self.session.port.setData(self.trigger)
                            core.wait(0.005)
                            self.session.port.setData(0)
                            self.timing_array.append(
                                [int(self.trigger), clock.getTime() - self.last_phase_time])
                    elif present_red_grating.opacity == 0:
                        if self.trigger is not green:
                            self.trigger = green
                            self.session.port.setData(self.trigger)
                            core.wait(0.005)
                            # checking time, can be removed #
#                            self.p = True
#                            print('-------trigger stimuli---------')
#                            print(clock.getTime())
                            #-------------------------#
                            self.timing_array.append(
                                [int(self.trigger), clock.getTime() - self.last_phase_time])
                            self.session.port.setData(0)

#        elif (self.phase == 4):
#            self.session.counter_left.text = self.parameters['percept_count']
#            self.session.counter_right.text = self.parameters['percept_count']
#
#            self.session.counter_instruction_left.draw()
#            self.session.counter_instruction_right.draw()
#            self.session.counter_left.draw()
#            self.session.counter_right.draw()

        # filp screen so everyting that has been drawn will be displayed
        super(MEG_BR_Trial, self).draw(self.p)
        self.p = False

    def event(self):

        for ev in event.getKeys():

            if len(ev) > 0:
                if ev in ['esc', 'escape', 'q']:
                    self.events.append(
                        [-99, self.session.clock.getTime() - self.start_time])
                    self.stopped = True
                    self.session.stopped = True
                    print ('run canceled by user')

                elif ev in ('1', '2', '3', '4', ' ', 't') and self.repeat != ev:
                    # these events have to be captured
                    if self.session.config['use_parallel'] == 1:
                        self.session.port.setData(ord(ev))
                        core.wait(0.005)
                        self.session.port.setData(0)
                        self.repeat = ev
                    if (self.phase == 0):
                        if self.ID > 0:
                            self.phase_forward()
                        elif ev == 't':
                            core.wait(3) #3 sec buffer after EEG recording starts
                            self.phase_forward() 
                    if (self.phase == 4):
                        if ev == '2':
                            self.parameters['percept_count'] -= 1
                        elif ev == '1':
                            self.parameters['percept_count'] += 1
                        # elif ev == '4':
                        #     self.stopped = True
                    if (self.phase == 2):
                        if ev in ('1', '2', '3'):
                            self.timing_array.append(
                                [int(ev), clock.getTime() - self.last_phase_time])
                                
            super(MEG_BR_Trial, self).key_event(ev)

    def run(self):
        if self.parameters['color_eye_combination'] == -1:
            self.session.red_grating_1.setPos(self.session.left_pos)
            self.session.green_grating_1.setPos(self.session.right_pos)
            self.session.red_grating_2.setPos(self.session.left_pos)
            self.session.green_grating_2.setPos(self.session.right_pos)
        if self.parameters['color_eye_combination'] == 1:
            self.session.red_grating_1.setPos(self.session.right_pos)
            self.session.green_grating_1.setPos(self.session.left_pos)
            self.session.red_grating_2.setPos(self.session.right_pos)
            self.session.green_grating_2.setPos(self.session.left_pos)

        super(MEG_BR_Trial, self).run()

    def phase_forward(self):
        if self.session.config['use_parallel'] == 1:
            self.session.port.setData(self.phase + 10)
            core.wait(0.005)
            self.session.port.setData(0)
        self.last_phase_time = clock.getTime()
        super(MEG_BR_Trial, self).phase_forward()


class Replay_MEG_BR_Trial(MEG_BR_Trial):
    def __init__(self, ti, config, parameters, *args, **kwargs):
        super(
            Replay_MEG_BR_Trial,
            self).__init__(
            phase_durations=phase_durations,
            parameters=parameters,
            *args,
            **kwargs)
