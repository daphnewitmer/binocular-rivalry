from __future__ import division
from exptools.core.session_test import EyelinkSession
from trial import MEG_BR_Trial

from ctypes import windll
#windll.LoadLibrary("C:\\PROGS\\inpoutx64.dll")

from psychopy import visual, clock, parallel, filters
import numpy as np
import os
import exptools
import json
import glob
import random
import pandas as pd
from copy import copy


class MEG_BR_Session(EyelinkSession):

    def __init__(self, *args, **kwargs):

        super(MEG_BR_Session, self).__init__(*args, **kwargs)

        config_file = os.path.join(os.path.abspath(
            os.getcwd()), 'default_settings.json')

        with open(config_file) as config_file:
            config = json.load(config_file) # This is it!! Here is where I change 

        self.config = config
        self.setup_stimuli()
        self.create_trials()

        self.stopped = False

    def create_trials(self):
        """creates trials by creating a restricted random walk through the display from trial to trial"""

        self.trial_parameters = [{'color_eye_combination': -1,  # ((i%2)*2)-1,
                                  #float((np.floor((i%4)/2)*2.0)-1.0),
                                  'motion_direction': 1,
                                  'report': 1,  # int(np.floor((i%8)/4)),
                                  # int(np.floor((i%16)/8)) ,
                                  'color_flicker_frequency_contingency': 1,
                                  'replay': self.config['replay']
                                  }]
        # random.shuffle(self.trial_parameters) #shuffles the trials randomly
        self.trials = [MEG_BR_Trial(ti=trial_id,
                                    config=self.config,
                                    screen=self.screen,
                                    session=self,
                                    parameters=parameters,
                                    tracker=self.tracker) for trial_id, parameters in enumerate(self.trial_parameters)]

        self.all_frame_opacities = np.array(
            [t.rg_opacity_indices for t in self.trials]).reshape((len(self.trial_parameters), -1))
        np.savetxt(self.output_file + '_frames.log', self.all_frame_opacities)

    def setup_stimuli(self):
        """setup_stimuli creates all stimuli that do not change from trial to trial"""

        self.left_pos = [-self.screen.size[0]/4 + self.deg2pix(self.config['x_offset_left_eye']),
                         self.deg2pix(self.config['y_offset_left_eye'])]

        self.right_pos = [self.screen.size[0]/4 + self.deg2pix(self.config['x_offset_right_eye']),
                          self.deg2pix(self.config['y_offset_right_eye'])]

        # fixations
        self.fixation_left = visual.GratingStim(self.screen,
                                                tex='sin',
                                                mask='raisedCos',
                                                size=self.deg2pix(
                                                    self.config['size_fixation_deg']),
                                                texRes=128,
                                                maskParams={
                                                    'fringeWidth': 0.2},
                                                color='white',
                                                sf=0,
                                                pos=self.left_pos)

        self.fixation_right = visual.GratingStim(self.screen,
                                                 tex='sin',
                                                 mask='raisedCos',
                                                 size=self.deg2pix(
                                                     self.config['size_fixation_deg']),
                                                 texRes=128,
                                                 maskParams={
                                                     'fringeWidth': 0.2},
                                                 color='white',
                                                 sf=0,
                                                 pos=self.right_pos)

        self.fixation_surround_left = visual.GratingStim(self.screen,
                                                         tex='sin',
                                                         mask='raisedCos',
                                                         size=self.deg2pix(
                                                             self.config['size_fixation_surround_deg']),
                                                         texRes=128,
                                                         maskParams={
                                                             'fringeWidth': 0.4},
                                                         color='black',
                                                         sf=0,
                                                         pos=self.left_pos)

        self.fixation_surround_right = visual.GratingStim(self.screen,
                                                          tex='sin',
                                                          mask='raisedCos',
                                                          size=self.deg2pix(
                                                              self.config['size_fixation_surround_deg']),
                                                          texRes=128,
                                                          maskParams={
                                                              'fringeWidth': 0.4},
                                                          color='black',
                                                          sf=0,
                                                          pos=self.right_pos)
        # BR gratings
        x, y = np.meshgrid(np.linspace(-self.config['BR_stim_size']*self.config['BR_stim_sf']*np.pi, self.config['BR_stim_size']*self.config['BR_stim_sf']*np.pi, 512, endpoint=True),
                           np.linspace(-self.config['BR_stim_size']*self.config['BR_stim_sf']*np.pi, self.config['BR_stim_size']*self.config['BR_stim_sf']*np.pi, 512, endpoint=True))

# New Version        
        # Create gratings
        red_grating_rad = np.sign(visual.filters.makeGrating(res=512, cycles=1.0)) # radial gratings
        red_grating_exp = np.sign(visual.filters.makeGrating(res=512, cycles=1.0, ori=90)) # angular gratings orthogonal to the radial one, hence orientation is 90 deg
        
        green_grating_rad = np.sign(visual.filters.makeGrating(res=512, cycles=2.0)) # changing the cycles will change how thin the angular slices are
        green_grating_exp = np.sign(visual.filters.makeGrating(res=512, cycles=1.0, ori=90))

        #create textures using numpy arrays
        red_grating1 = -np.ones((512, 512, 3)) 
        red_grating1[...,0] = red_grating_exp * red_grating_rad # update the red dimesion (3rd dimension index = 0) 
        #create textures using numpy arrays
        red_grating2 = -np.ones((512, 512, 3)) 
        red_grating2[...,0] = -red_grating1[...,0]    
                
        #create textures using numpy arrays
        green_grating1 = -np.ones((512, 512, 3)) 
        green_grating1[...,1] = -green_grating_exp * green_grating_rad # update the green dimesion (3rd dimension index = 1) 
        #create textures using numpy arrays
        green_grating2 = -np.ones((512, 512, 3)) 
        green_grating2[...,1] = -green_grating1[...,1]    
        
        green_grating1[green_grating1[...,1]==1,1] = 0
        green_grating2[green_grating2[...,1]==1,1] = 0
        red_grating1[red_grating1[...,0]==-1,0] = -0.3
        red_grating2[red_grating2[...,0]==-1,0] = -0.3
        
        self.red_grating_1 = visual.RadialStim(self.screen,
                                               tex=-red_grating1,                                               
                                               radialCycles=3,
                                               angularCycles=4,
                                               mask='raisedCos',
                                               size=self.deg2pix(
                                                   self.config['BR_stim_size']),
                                               texRes=512,
                                               maskParams={'fringeWidth': 0.2},
                                               contrast=1,
                                               color='red',
                                               colorSpace='hsv',
                                               interpolate=True
                                               )
        self.green_grating_1 = visual.RadialStim(self.screen,
                                               tex=-green_grating1,                                               
                                               radialCycles=3,
                                               angularCycles=4,
                                               mask='raisedCos',
                                               size=self.deg2pix(
                                                   self.config['BR_stim_size']),
                                               texRes=512,
                                               maskParams={'fringeWidth': 0.2},
                                               contrast=1,
                                               color='black',
                                               colorSpace='hsv',
                                               interpolate=True)

        self.red_grating_2 = visual.RadialStim(self.screen,
                                               tex=-red_grating2,                                               
                                               radialCycles=3,
                                               angularCycles=4,
                                               mask='raisedCos',
                                               size=self.deg2pix(
                                                   self.config['BR_stim_size']),
                                               texRes=512,
                                               maskParams={'fringeWidth': 0.2},
                                               contrast=1,
                                               color='red',
                                               colorSpace='hsv',
                                               interpolate=True
                                               )
        self.green_grating_2 = visual.RadialStim(self.screen,
                                               tex=-green_grating2,                                               
                                               radialCycles=3,
                                               angularCycles=4,
                                               mask='raisedCos',
                                               size=self.deg2pix(
                                                   self.config['BR_stim_size']),
                                               texRes=512,
                                               maskParams={'fringeWidth': 0.2},
                                               contrast=1,
                                               color='black',
                                               colorSpace='hsv',
                                               interpolate=True)
                                               
#      #older version
#      
#        self.red_grating_1 = visual.RadialStim(self.screen,
#                                                   tex='sqrXsqr',
#                                                   radialCycles=3,
#                                                   angularCycles=4,
#                                                   # angularPhase=3.14/4.0,
#                                                   # radialPhase=3.14/4.0,
#                                                   mask='raisedCos',
#                                                   size=self.deg2pix(
#                                                       self.config['BR_stim_size']),
#                                                   texRes=512,
#                                                   maskParams={'fringeWidth': 0.2},
#                                                   contrast=1,
#                                                   color='red',
#                                                   colorSpace='black',
#                                                   interpolate=True)
#    
#        self.green_grating_1 = visual.RadialStim(self.screen,
#                                                     tex='sqrXsqr',
#                                                     radialCycles=2,
#                                                     angularCycles=8,
#                                                     # angularPhase=3.14/4.0,
#                                                     # radialPhase=3.14/4.0,
#                                                     mask='raisedCos',
#                                                     size=self.deg2pix(
#                                                         self.config['BR_stim_size']),
#                                                     texRes=512,
#                                                     maskParams={
#                                                         'fringeWidth': 0.2},
#                                                     color='green',
#                                                     contrast=1,
#                                                     interpolate=True)
#        self.green_grating_1.setOpacity(self.config['BR_stim_RG_ratio'])
#    
#        self.red_grating_2 = visual.RadialStim(self.screen,
#                                                   tex='sqrXsqr',
#                                                   radialCycles=3,
#                                                   angularCycles=4,
#                                                   # angularPhase=3.14,
#                                                   # radialPhase=3.14/2.0,
#                                                   mask='raisedCos',
#                                                   size=self.deg2pix(
#                                                       self.config['BR_stim_size']),
#                                                   texRes=512,
#                                                   maskParams={'fringeWidth': 0.2},
#                                                   contrast=-1,
#                                                   color='red',
#                                                   colorSpace='white',
#                                                   interpolate=True)
#    
#        self.green_grating_2 = visual.RadialStim(self.screen,
#                                                     tex='sqrXsqr',
#                                                     radialCycles=2,
#                                                     angularCycles=8,
#                                                     # angularPhase=3.14,
#                                                     # radialPhase=3.14/2.0,
#                                                     mask='raisedCos',
#                                                     size=self.deg2pix(
#                                                         self.config['BR_stim_size']),
#                                                     texRes=512,
#                                                     maskParams={
#                                                         'fringeWidth': 0.2},
#                                                     color='green',
#                                                     contrast=-1,
#                                                     interpolate=True)
#        self.green_grating_2.setOpacity(self.config['BR_stim_RG_ratio'])
    

        # fusion aid background
        bg_tex = (2*np.sqrt(np.sqrt(self.create_bg_texture(
            tex_size=self.config['background_tex_size'], amplitude_exponent=self.config['background_amplitude_exponent']))))-1
        self.bg_stimulus_left = visual.GratingStim(self.screen,
                                                   tex=bg_tex,
                                                   mask=None,
                                                   size=[self.deg2pix(self.config['background_stim_width']), self.deg2pix(
                                                       self.config['background_stim_height'])],
                                                   texRes=bg_tex.shape[0],
                                                   color='white',
                                                   pos=self.left_pos)

        self.bg_stimulus_right = visual.GratingStim(self.screen,
                                                    tex=bg_tex,
                                                    mask=None,
                                                    size=[self.deg2pix(self.config['background_stim_width']), self.deg2pix(
                                                        self.config['background_stim_height'])],
                                                    texRes=bg_tex.shape[0],
                                                    color='white',
                                                    pos=self.right_pos)

        # backgrounds to draw the gratings over, so that textured background doesn't flow behind the gratings.
        self.grating_bg_left = visual.GratingStim(self.screen,
                                                  tex='sin',
                                                  mask='raisedCos',
                                                  size=self.deg2pix(
                                                      self.config['BR_stim_mask_size']),
                                                  texRes=512,
                                                  color='black',
                                                  sf=0,
                                                  maskParams={
                                                      'fringeWidth': 0.2},
                                                  pos=self.left_pos)

        self.grating_bg_right = visual.GratingStim(self.screen,
                                                   tex='sin',
                                                   mask='raisedCos',
                                                   size=self.deg2pix(
                                                       self.config['BR_stim_mask_size']),
                                                   texRes=512,
                                                   color='black',
                                                   sf=0,
                                                   maskParams={
                                                       'fringeWidth': 0.2},
                                                   pos=self.right_pos)

        counter_instruction = ''
        self.counter_instruction_left = visual.TextStim(self.screen,
                                                        text=counter_instruction,
                                                        font='Helvetica Neue',
                                                        pos=self.left_pos,
                                                        italic=True,
                                                        height=20,
                                                        alignHoriz='center',
                                                        color=(1, 0, 0))

        self.counter_instruction_right = visual.TextStim(self.screen,
                                                         text=counter_instruction,
                                                         font='Helvetica Neue',
                                                         pos=self.right_pos,
                                                         italic=True,
                                                         height=20,
                                                         alignHoriz='center',
                                                         color=(1, 0, 0))

        counter_left_pos = copy(self.left_pos)
        counter_left_pos[1] -= self.deg2pix(1)
        self.counter_left = visual.TextStim(self.screen,
                                            text=7,
                                            font='Helvetica Neue',
                                            pos=counter_left_pos,
                                            italic=True,
                                            height=20,
                                            alignHoriz='center',
                                            color=(1, 1, 1))

        counter_right_pos = copy(self.right_pos)
        counter_right_pos[1] -= self.deg2pix(1)
        self.counter_right = visual.TextStim(self.screen,
                                             text=7,
                                             font='Helvetica Neue',
                                             pos=counter_right_pos,
                                             italic=True,
                                             height=20,
                                             alignHoriz='center',
                                             color=(1, 1, 1))

    def create_bg_texture(self, tex_size=1024, amplitude_exponent=1.0):

        t2 = int(tex_size/2)
        X, Y = np.meshgrid(np.linspace(-t2, t2, tex_size, endpoint=True),
                           np.linspace(-t2, t2, tex_size, endpoint=True))
        ecc = np.sqrt(X**2 + Y**2)
        ampl_spectrum = np.fft.fftshift(ecc**-amplitude_exponent, (0, 1))
        phases = np.random.randn(tex_size, tex_size) * 2 * np.pi
        texture = np.zeros((tex_size, tex_size))

        compl_f = ampl_spectrum * \
            np.sin(phases) + 1j * ampl_spectrum * np.cos(phases)
        texture = np.fft.ifft2(compl_f).real
        # center at zero
        texture -= texture.mean()
        # scale and clip to be within [-1,1]
        texture /= texture.std()*6.666
        # texture += 0.5
        texture[texture < 0] = 0
        texture[texture > 1] = 1

        return texture

    def run(self):
        """run the session"""
#        print("we actually start")
#        self.port = parallel.ParallelPort(address=0x3050)
#        self.port.setData(255)
        if self.config['use_parallel'] == 1:
            #LPT1 = 0x0378 # or 0x03BC
            # LPT2 = 0x0278 # or 0x0378
            # LPT3 = 0x0278
            self.port = parallel.ParallelPort(address=0x3050)
            self.port.setData(0)

        # cycle through trials

        for trial_id, trial in enumerate(self.trials):
            print('about to run the trial')
            trial.ID = trial_id
            trial.run()

            if self.stopped == True:
                break

        self.close()

    def close(self):
        if self.trial_parameters[0]['replay'] == 0:  # we save
            df = pd.DataFrame(
                self.trials[0].timing_array, columns=['ID', 'Time'])
            df.to_csv(os.path.join(
                os.path.split(self.output_file)[0], self.subject_initials + '_' + str(self.index_number) + '.tsv'), sep='\t')
        super(MEG_BR_Session, self).close()
