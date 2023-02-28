import json
import os
from exptools.core.session_test import EyelinkSession
from psychopy import visual
from psychopy.hardware.keyboard import Keyboard
import numpy as np
from psychopy import gui

class Adjust_Stimuli_Pos(EyelinkSession):
    def __init__(self, *args, **kwargs):
        
        super(Adjust_Stimuli_Pos, self).__init__('pilot', None, None, None, 1, *args, **kwargs)
        
        config_file = os.path.join(os.path.abspath(os.getcwd()), 'default_settings.json')
        with open(config_file) as config_file: 
            self.config = json.load(config_file) 
            
        self.left_pos = [-self.screen.size[0]/4 + self.deg2pix(self.config['x_offset_left_eye']),
                                 self.deg2pix(self.config['y_offset_left_eye'])]

        self.right_pos = [self.screen.size[0]/4 + self.deg2pix(self.config['x_offset_right_eye']),
                                  self.deg2pix(self.config['y_offset_right_eye'])]
        self.create_stimuli()
        self.draw_stimuli()
                                  
    def create_stimuli(self):
        bg_tex = (2*np.sqrt(np.sqrt(self.create_bg_texture(tex_size=self.config['background_tex_size'], 
            amplitude_exponent=self.config['background_amplitude_exponent']))))-1
            
        this_instruction_string = """\n\nPlease keep fixation on the dot"""
            
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
        self.instruction_left = visual.TextStim(self.screen,
                                                text=this_instruction_string,
                                                font='Helvetica Neue',
                                                pos=self.left_pos,
                                                italic=True,
                                                height=20,
                                                alignHoriz='center',
                                                color=(1, 0, 0))
        self.instruction_right = visual.TextStim(self.screen,
                                                 text=this_instruction_string,
                                                 font='Helvetica Neue',
                                                 pos=self.right_pos,
                                                 italic=True,
                                                 height=20,
                                                 alignHoriz='center',
                                                 color=(1, 0, 0))
                                                 
    def draw_stimuli(self):
        
        event = Keyboard()
        while True:
            keys = event.getKeys()
            self.bg_stimulus_left.draw()
            self.bg_stimulus_right.draw()
            self.grating_bg_left.draw()
            self.grating_bg_right.draw()
            self.fixation_left.draw()
            self.fixation_right.draw()
            self.instruction_left.draw()
            self.instruction_right.draw()
            self.screen.flip()
            
            if 'a' in keys:
                self.config['x_offset_left_eye'] += -1.0
                self.left_pos = [-self.screen.size[0]/4 + self.deg2pix(self.config['x_offset_left_eye']),
                                 self.deg2pix(self.config['y_offset_left_eye'])]
                self.create_stimuli()
            if 'd' in keys:
                self.config['x_offset_left_eye'] += 1.0
                self.left_pos = [-self.screen.size[0]/4 + self.deg2pix(self.config['x_offset_left_eye']),
                                 self.deg2pix(self.config['y_offset_left_eye'])]
                self.create_stimuli()
            if 'left' in keys:
                self.config['x_offset_right_eye'] += -1.0
                self.right_pos = [self.screen.size[0]/4 + self.deg2pix(self.config['x_offset_right_eye']),
                                  self.deg2pix(self.config['y_offset_right_eye'])]
                self.create_stimuli()
            if 'right' in keys:
                self.config['x_offset_right_eye'] += 1.0
                self.right_pos = [self.screen.size[0]/4 + self.deg2pix(self.config['x_offset_right_eye']),
                                  self.deg2pix(self.config['y_offset_right_eye'])]
                self.create_stimuli()
            if 'q' in keys:
                self.save_position()
                break
                
    def save_position(self):
        self.screen.close()
        dlg = gui.Dlg(title='Save Position')
        dlg.addField('Save Position?', choices=["Yes", "No"])
        data = dlg.show()
        
        if data[0] == 'Yes':
            with open('default_settings.json', 'w') as outfile:
                json.dump(self.config, outfile, indent=2)
                print('save')
        else:
            print('position not saved')
        
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
            

