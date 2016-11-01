from MesaProfile import MesaProfile

# The following is the original syntax for getting a star profile
mesa = MesaProfile()
mesa.setInProfileName('profile.data')
mesa.readProfile() # or readHistory() if it's a history file
mstar = mesa.getStar() # mstar is an OrderedDict

# The following is the new syntax (both work) for profile or history files
# so long as the filename contains either the word 'profile' or 'history'
mesa = MesaProfile('profile.data')
mstar = mesa.star # mesa.star is the OrderedDict



