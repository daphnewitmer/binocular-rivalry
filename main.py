import sys
from session import MEG_BR_Session
from sys import platform
from psychopy import gui # This is to invoke a dialog box to enter session details
from position import Adjust_Stimuli_Pos


if platform == "darwin":
    import appnope
    from psychopy.platform_specific.darwin import rush
elif platform == "linux2":
    
    from psychopy.platform_specific.linux import rush


def main():

    # dialog box
    Pinfo = gui.Dlg(title='Participant initials')
    Pinfo.addField('Enter Participant Initials: ', 'Participant 1')
    Pinfo.addField('Enter Run Number: ')
    Pinfo.addField('Run Type:', choices=["Run1", "Run2", "Localizer"])
    Pinfo.addField('Color Eye Combination:', choices=["red-green", "green-red"])
    Pinfo.addField('Adjust Positions:', choices=["No", "Yes"])
    Pinfo.show()
    
    if Pinfo.OK:
        Pdat = Pinfo.data
        initials = Pdat[0]
        run_nr = Pdat[1]
        run_type = Pdat[2]
        color_eye_combination = -1 if Pdat[3] == "red-green" else 1
        adjust_pos = Pdat[4]
    
    if adjust_pos == "Yes": 
        pos = Adjust_Stimuli_Pos(subject_initials=initials, index_number=run_nr, tracker_on=False)
    else:
        ts = MEG_BR_Session(subject_initials=initials, index_number=run_nr, tracker_on=False)
        ts.run(color_eye_combination)

if __name__ == '__main__':
    main()
