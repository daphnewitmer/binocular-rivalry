import sys
from session import MEG_BR_Session
from sys import platform
from psychopy import gui #dialog box
from position import Adjust_Stimuli_Pos #Stim position
import pandas as pd
import numpy as np

# import dependencies for non-Windows OS
if platform == "darwin":
    import appnope
    from psychopy.platform_specific.darwin import rush
elif platform == "linux2":
    from psychopy.platform_specific.linux import rush

def main():
    
    # dataframe to convert dropdown names to labels. Don't change labels!
    run_type_df = pd.DataFrame({ 
        'names' :["No Report 1","No Report 2", "Self Report 1","Self Report 2", "LocFixTask 1", "LocFixTask 2", "Localizer 1", "Localizer 2"],
        'labels': ["no_rep_1","no_rep_2", "self_rep_1","self_rep_2", "loc_fix_task_1", "loc_fix_task_2", "loc_1", "loc_2"]
    })

    # Run info - Dialog box
    Pinfo = gui.Dlg(title='Run Information')
    Pinfo.addField('Enter Participant Number: ', choices= ["Pilot", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32"])
    Pinfo.addField('Select Block', choices= ["Practice","Baseline", "FA", "OM"])
    Pinfo.addField('Select Run Type', choices= run_type_df['names'].values.tolist())
    Pinfo.addField('Choose Color Side', choices=["Red Green", "Green Red"]) # -1:red-green; 1:green-red
    Pinfo.addField('Adjust Stimulus Positions?', choices= ["No", "Yes"])
    Pinfo.show()
    
    if Pinfo.OK:
        # save data from dropdown
        Pdat = Pinfo.data
        participant_nr = Pdat[0]
        block_type = Pdat[1]
        i = run_type_df.index[run_type_df['names'] == Pdat[2]]
        run_type = run_type_df['labels'][i].values[0]
        color_eye_combination = -1 if Pdat[3] == "Red Green" else 1
        adjust_pos = Pdat[4]

        if adjust_pos == "Yes": 
            # adjust stimulus panels positions
            pos = Adjust_Stimuli_Pos()
        else:
            # start experiment
            ts = MEG_BR_Session(participant_nr=participant_nr, block_type=block_type, run_type=run_type, color_combi=color_eye_combination, tracker_on=False)
            ts.run()

if __name__ == '__main__':
    main()
