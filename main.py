import sys
from session import MEG_BR_Session
from sys import platform
from psychopy import gui #This is to invoke a dialog box to enter session details


if platform == "darwin":
    import appnope
    from psychopy.platform_specific.darwin import rush
elif platform == "linux2":
    
    from psychopy.platform_specific.linux import rush


def main():
#    initials = 'RL' #sys.argv[1] #Testing
#    run_nr = 1 #sys.argv[2] #Testing
#    initials = input('Your initials: ')
#    run_nr = int(input('Run number: '))


    # dialog box
    #Initials
    Pinfo = gui.Dlg(title='Participant initials')
    Pinfo.addField('Enter Participant Initials: ')
    Pinfo.show()
    if Pinfo.OK:
        Pdat = Pinfo.data
        initials = Pdat[0]
    
#    # Trial condition
#    Pinfo = gui.Dlg(title='Condition Type')
#    Pinfo.addField('Select Condition Type: ', choices=["Practice", "Control", "FA", "OM"])
#    Pinfo.show()
#    if Pinfo.OK:
#        Pdat = Pinfo.data
#        condition = Pdat[0]
        
    #Run Number
    Pinfo = gui.Dlg(title='Run Number')
    Pinfo.addField('Enter Run Number: ')
    Pinfo.show()    
    if Pinfo.OK:
        Pdat = Pinfo.data
        run_nr = Pdat[0]
        

#        
#    scanner = input('Are you in the scanner (y/n)?: ')
#    track_eyes = raw_input('Are you recording gaze (y/n)?: ')
#    if track_eyes == 'y':
#        tracker_on = True
#    elif track_eyes == 'n':
#        tracker_on = False

    # initials = 'tk'
    # run = 13
    #if platform == "darwin":
    #    appnope.nope()
    #rush()

    ts = MEG_BR_Session(subject_initials=initials, index_number=run_nr, tracker_on=False)
    ts.run()

if __name__ == '__main__':
    main()