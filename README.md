```
                                      BIOSUR
```
```
           *                *          *            *        *                  *      
          / /\             /\ \       /\ \         / /\     /\_\               /\ \    
         / /  \            \ \ \     /  \ \       / /  \   / / /         *    /  \ \   
        / / /\ \           /\ \*\   / /\ \ \     / / /\ \__\ \ \__      /\_\ / /\ \ \  
       / / /\ \ \         / /\/_/  / / /\ \ \   / / /\ \___\\ \___\    / / // / /\ \_\ 
      / / /\ \_\ \       / / /    / / /  \ \_\  \ \ \ \/___/ \__  /   / / // / /_/ / / 
     / / /\ \ \___\     / / /    / / /   / / /   \ \ \       / / /   / / // / /__\/ /  
    / / /  \ \ \__/    / / /    / / /   / / /_    \ \ \     / / /   / / // / /_____/   
   / / /____\_\ \  ___/ / /__  / / /___/ / //_/\__/ / /    / / /___/ / // / /\ \ \     
  / / /__________\/\__\/_/___\/ / /____\/ / \ \/___/ /    / / /____\/ // / /  \ \ \    
  \/_____________/\/_________/\/_________/   \_____\/     \/_________/ \/_/    \_\/     
```

The purpose of this repo is to automatize and refactor the  CRECK characterization method for biomass.

The codes takes as input the elemental composition of a biomass sample in terms of Carbon (C) and Hydrogen (H) in Dry Ash Free (D.A.F) basis wt (-). Oxygen (O) content is calculated by difference, such that C + O + H = 1. 

Further input parameters are the content of ashes (ASH) and humidity (MOIST) wt (-).
You also need to specify the kind of biomass you ara analyizing, possible options are:  
+ Other
+ Grass
+ Hardwood
+ Softwood

The code then returns the composition in terms of the component taken  as input in the CRECK kinetick scheme for biomasses. These include:

+ Cellulose: CELL
+ Lignin: LIGO, LIGC and LIGH
+ Hemicellulose: XYGR or XYHW or GMSW, chosen based on the type of biomass

See the following publication for more informations:
    TODO
