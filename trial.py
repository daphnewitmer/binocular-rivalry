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


class MEG_BR_Trial(Trial):
   
    # Define the display framework upon which stimulus is presented
    def __init__(self, ti, config, parameters, *args, **kwargs):

        self.ID = ti
        self.repeat = 0
        # self.parameters = parameters

        phase_durations = [100000,
                           config['fixation_duration'],
                           config['stimulus_duration'], # Stimulus duration has to be adjusted but how? - in the default_settings.JSON file
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
        
        # initialize variables?
        self.timing_array = []
        self.frame = 0

        self.red_flicker_frame, self.green_flicker_frame = 0, 0
        self.red_orientation, self.green_orientation = 0, 0

        safety_margin = 10.0
        nr_frames_in_stimulus = int(
            (self.parameters['stimulus_duration'] + safety_margin) * self.parameters['refresh_frequency'])
        frame_times = np.linspace(
            0, self.parameters['stimulus_duration'] + safety_margin, nr_frames_in_stimulus, endpoint=False)

        if parameters['replay'] == 1:

            self.behavior_df = pd.read_csv(os.path.join(
                os.path.split(self.session.output_file)[0], self.session.subject_initials + '.tsv'), sep='\t')

            rp_percept_per_frame = np.ones(nr_frames_in_stimulus) * 2
            time_per_frame = np.arange(0, nr_frames_in_stimulus/float(
                self.parameters['refresh_frequency']), 1/float(self.parameters['refresh_frequency']))

            for percept, time in zip(self.behavior_df['ID'], self.behavior_df['Time']):
                rp_percept_per_frame[time_per_frame > time] = (percept-1)/2.0

            # the number multiplied by refresh frequency specifies the 'duration' of the
            # transition between states. Make it 0, and they're instantaneous.
            smoothed_rp_percept_per_frame = gaussian_filter(
                rp_percept_per_frame, 0.125 * self.parameters['refresh_frequency'])

            self.rg_opacity_indices = np.array([smoothed_rp_percept_per_frame, 1-smoothed_rp_percept_per_frame]) * np.array([
                1, self.parameters['BR_stim_RG_ratio']])[:, np.newaxis]
        else:
            self.rg_opacity_indices = np.ones((2, nr_frames_in_stimulus)) * np.array(
                [1, self.parameters['BR_stim_RG_ratio']])[:, np.newaxis]

        self.rg_opacity_indices = np.clip(self.rg_opacity_indices, 0, 1)

        self.parameters['percept_count'] = np.random.choice([5, 6, 7, 8])
    
    # Define Stimulus
    def create_stimuli(self):

        if self.parameters['report'] == 1:
            this_instruction_string = """\n\nPlease keep fixation on the dot"""
        else:
            this_instruction_string = """\n\nPlease keep fixation on the dot"""

        if self.ID == 0:
            this_instruction_string = this_instruction_string.replace(
                "Press any key to start", "Trial will begin soon")

        self.instruction_left = visual.TextStim(self.screen,
                                                text=this_instruction_string,
                                                font='Helvetica Neue',
                                                pos=self.session.left_pos,
                                                italic=True,
                                                height=20,
                                                alignHoriz='center',
                                                color=(1, 0, 0))
        self.instruction_right = visual.TextStim(self.screen,
                                                 text=this_instruction_string,
                                                 font='Helvetica Neue',
                                                 pos=self.session.right_pos,
                                                 italic=True,
                                                 height=20,
                                                 alignHoriz='center',
                                                 color=(1, 0, 0))

    # Define how to draw the stimulus 
    def draw(self, *args, **kwargs):

        self.session.bg_stimulus_left.draw()
        self.session.bg_stimulus_right.draw()

        self.session.grating_bg_left.draw()
        self.session.grating_bg_right.draw()
        
        if self.phase == 2:  # stimulus
            pres_time = clock.getTime() # timestammp
            time_since_phase = pres_time - self.last_phase_time
            
            # measure the number of frames that have passed 
            frame_since_phase = int(
                time_since_phase * self.parameters['refresh_frequency'])
            self.frame = frame_since_phase # current frame number 
            
            # Stim Flicker Frequency; Also check: https://stackoverflow.com/questions/37469796/where-can-i-find-flickering-functions-for-stimuli-on-psychopy-and-how-do-i-use
            red_ff = [self.parameters['high_flicker_period_frames'], self.parameters['low_flicker_period_frames']
                      ][self.parameters['color_flicker_frequency_contingency']] # color_flicker_frequency_contingency is set to 1 in session.py
                      # In Python: [16,12][1] = 12; hence, if color_flicker_frequency_contingency=1, the second value out of the two is chosen
                      
            green_ff = [self.parameters['high_flicker_period_frames'], self.parameters['low_flicker_period_frames']
                        ][1-self.parameters['color_flicker_frequency_contingency']]
                        # In Python: [16,12][0] = 16; hence, if [1 - color_flicker_frequency_contingency]=0, the first value out of the two is chosen
                        
                        # Also, in the default_Settings.json file, make sure the following values are set for a monitor refresh rate of 240Hz:
                        #	"high_flicker_period_frames": 8,	"low_flicker_period_frames": 10,
                        # This will ensure the left stimulus flickers at 12 Hz and the right at 15 Hz
                        
            flicker_level_red = int(np.floor(self.frame % (red_ff*2) / red_ff))
            flicker_level_green = int(
                np.floor(self.frame % (green_ff*2) / green_ff))

# I assume the following couple of line use an older method to calculate flicker level
#            flicker_level_red = int((self.frame%red_ff)==0) # changing the value of the 
#            flicker_level_green = int((self.frame%green_ff)==0)

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
            
            present_red_grating.draw()
            present_green_grating.draw()

#            self.frame += 1

        self.session.fixation_surround_left.draw()
        self.session.fixation_surround_right.draw()

        self.session.fixation_left.draw()
        self.session.fixation_right.draw()

        # draw additional stimuli:
        if (self.phase == 0):
            self.instruction_left.draw()
            self.instruction_right.draw()
        elif (self.phase == 4):
            self.session.counter_left.text = self.parameters['percept_count']
            self.session.counter_right.text = self.parameters['percept_count']

            self.session.counter_instruction_left.draw()
            self.session.counter_instruction_right.draw()
            self.session.counter_left.draw()
            self.session.counter_right.draw()

        super(MEG_BR_Trial, self).draw()

    def event(self):

        for ev in event.getKeys():

            if len(ev) > 0:
                if ev in ['esc', 'escape', 'q']:
                    self.events.append(
                        [-99, self.session.clock.getTime() - self.start_time])
                    self.stopped = True
                    self.session.stopped = True
                    print ('run canceled by user') #Parantheses added by Surya

                elif ev in ('1', '2', '3', '4', ' ', 't') and self.repeat != ev:
                    # these events have to be captured
                    if self.session.config['use_parallel'] == 1:
                        print(ord(ev))
                        self.session.port.setData(ord(ev))
                        print(self.session.port.readData())
                        core.wait(0.005)
                        self.session.port.setData(0)
                        self.repeat = ev
                    if (self.phase == 0):
                        if self.ID > 0:
                            self.phase_forward()
                        elif ev == 't':
                            self.phase_forward() # Press 't' to start the session
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

    def run(self, color_eye_combination):
        if color_eye_combination == -1:
            self.session.red_grating_1.setPos(self.session.left_pos)
            self.session.green_grating_1.setPos(self.session.right_pos)
            self.session.red_grating_2.setPos(self.session.left_pos)
            self.session.green_grating_2.setPos(self.session.right_pos)
        if color_eye_combination == 1:
            self.session.red_grating_1.setPos(self.session.right_pos)
            self.session.green_grating_1.setPos(self.session.left_pos)
            self.session.red_grating_2.setPos(self.session.right_pos)
            self.session.green_grating_2.setPos(self.session.left_pos)

        super(MEG_BR_Trial, self).run()

    def phase_forward(self):
        if self.session.config['use_parallel'] == 1:
            self.session.port.setData(self.phase + 10)
            print(self.session.port.readData())
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
