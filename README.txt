
##################################################
## Data Respository
##################################################


## -- InputData ----------------------------------                                    

1. EmissionFactor
   
   a. EF_non_NOx.csv
       # emission factors for CO2, SO2, SO4, OC, EC, NH3, NMVOC
   
   b. EF_NOx.csv
       # emission factors for NOx
       

2. BaselineMortality
   
   a. Location_MortailityRate_25plus_LRI.csv
       # baseline mortality for lower respiratory infections, by area
   
   b. Location_MortailityRate_25plus_NCD.csv
       # baseline mortality for non-communicable diseases, by area


3. Population
   
   a. gpw_v4_population_count_adjusted_rev11_30_min.nc
       # global gridded population
   
   b. geo_pop_25plus_ratio_2015.nc4
       # age profile by area



## -- ResultData ---------------------------------                                 

1. ShipEmissionHourly
    # hourly ship emissions caculated in this study based on AIS data
    # available to download at ......


2. ShipEmissionAnnual
    # aggregated annual ship emissions caculated in this study based on AIS data
    
    a. EM2015_%scenario_%sector
        # scenario: 
                BL  : baseline
                S1N0: 0.5% Sulphur Cap
                S2N0: 0.1% Sulphur Cap
                S1N1: Tier III NOx Standard
        # sector: 
                I   : emissions from international vessels only
                D   : emissions from domestic vessels only
                ID  : emissions from all vessels


3. GEOSChemMonthlyPM
    # monthly-averaged PM2.5 concentration simulated by GEOS-Chem modeling
    
    a. ../%scenario_%sector/GEOSChem.AerosolMass.%year%month_0000z.nc4
        # scenario: 
                BL    : baseline
                S1N0  : 0.5% Sulphur Cap
                S2N0  : 0.1% Sulphur Cap
                S1N1  : Tier III NOx Standard
        # sector: 
                I     : emissions from international vessels and non-ship sector
                D     : emissions from domestic vessels and non-ship sector
                ID    : emissions from all vessels and non-ship sector
                NoShip: emissions from non-ship sector only


4. GEOSChemAnnualPM
    # processed annual-averaged PM2.5 concentration, by simulations
    # simulations include: 
                BL_I     : baseline scenario, emissions from international vessels and non-ship sector 
                BL_D     : baseline scenario, emissions from domestic vessels and non-ship sector
                BL_ID    : baseline scenario, emissions from all vessels and non-ship sector
                BL_NoShip: baseline scenario, emissions from non-ship sector only
                S1N0_ID  : 0.5% Sulphur Cap scenario, emissions from all vessels and non-ship sector
                S2N0_ID  : 0.1% Sulphur Cap scenario, emissions from all vessels and non-ship sector
                S1N1_ID  : Tier III NOx Standard scenario, emissions from all vessels and non-ship sector
    
    a. YAVG_Conc_PM25_%simulation
        # annual average PM concentration for each simulation 
    
    b. YAVG_Conc_PM25_%simulation1_%simulation2 
        # difference of annual average PM concentration between simulations (simulation 1 - simulation 2)


5. HealthResult
    # mortality results, by simulations
    # simulations include: 
                BL_I     : baseline scenario, emissions from international vessels and non-ship sector 
                BL_D     : baseline scenario, emissions from domestic vessels and non-ship sector
                BL_ID    : baseline scenario, emissions from all vessels and non-ship sector
                BL_NoShip: baseline scenario, emissions from non-ship sector only
                S1N0_ID  : 0.5% Sulphur Cap scenario, emissions from all vessels and non-ship sector
                S2N0_ID  : 0.1% Sulphur Cap scenario, emissions from all vessels and non-ship sector
                S1N1_ID  : Tier III NOx Standard scenario, emissions from all vessels and non-ship sector
    
    a. Mortality_GEMM_NCD_PM25_%simulation.nc
        # mortality caused by NCD
    
    b. Mortality_GEMM_LRI_PM25_%simulation.nc
        # mortality caused by LRI: 
    
    c. Mortality_GEMM_NCD_LRI_PM25_%simulation.nc
        # totaly mortality caused by NCD+LRI
    
    d. Mortality_GEMM_NCD_LRI_PM25_%simulation1_%simulation2.nc
        # mortality difference between simulations (simulation1 - simulation2)


##################################################
## Scripts for data processing and figures
##################################################

Scripts:

1. GEOSChem setting
   # simulate PM2.5 concentration based on emissions
   # example simulation: BL_ID
   # for other simulations, just change the data directory
   
   a. HEMCO
   
   b. ......
 
 
2. to calculate health impact
   a. Data_HealthResult.py 
       # to estiamte mortality from PM2.5 concentration


3. to make plots:

   a. plot_emission.py  
       #  to generate spatial maps displaying emissions  (Figure 1)

   b. plot_pm_map.py
       # to generate spatial maps displaying PM2.5 concentration (Figure 2 & 3)

   c. plot_gemm_map.py
       # to generate spatial maps displaying mortality (Figure 4 & 5)

   



##################################################
## Figures
##################################################

diretory = ./Figure/

1. Fig_EM_%emission_%secenario_%sector (eps/svg/png/pdf)
   # Figure 1
   
   a. Fig_EM_CO2_BL_I
       # geographical distribution of CO2 emissions from maritime shipping in 2015 by international vessels
   
   b. Fig_EM_CO2_BL_D
       # geographical distribution of CO2 emissions from maritime shipping in 2015 by domestic vessels


2. Fig_GC_PM_%simulation1_%simulation2 (eps/svg/png/pdf)
   
   # Figure 2, Figure 3

   a. Fig_GC_PM_BL_ID_BL_D (Figure 2a)
       # Simulated annual-mean surface PM2.5 concentrations attributed to international vessels under the Baseline policy scenario
       # calculated by PM difference between two simulations (BL_ID - BL_D) 
   
   b. Fig_GC_PM_BL_ID_BL_I (Figure 2b)
       # Simulated annual-mean surface PM2.5 concentrations attributed to domestic vessels under the Baseline policy scenario
       # calculated by PM difference between two simulations (BL_ID - BL_I) 

   c. Fig_GC_PM_BL_ID_S1N0_ID (Figure 3a)
       # Reduction in annual-mean PM2.5 concentration due to 0.5% Sulphur Cap; 
       # calculated by PM difference between two simulations (BL_ID - S1N0_ID) 
       
   d. Fig_GC_PM_S1N0_ID_S2N0_ID (Figure 3b)
       # Reduction in annual-mean PM2.5 concentration due to 0.1% Sulphur Cap; 
       # calculated by PM difference between two simulations (S1N0_ID - S2N0_ID) 
       
   e. Fig_GC_PM_S1N0_ID_S1N1_ID (Figure 3c)
       # Reduction in annual-mean PM2.5 concentration due to Tier III NOx Standard; 
       # calculated by PM difference between two simulations (S1N0_ID - S1N1_ID) 
       

3. Fig_GEMM_NCD_LRI_%simulation1_%simulation2 (eps/svg/png/pdf)
   # Figure 4, Figure 5

   a. Fig_GEMM_NCD_LRI_BL_ID_BL_D (Figure 4a)
       # Global distribution of mortality (GEMM NCD+LRI) associated with ship-related PM2.5, due to emissions from international vessels
       # calculated by mortality difference between two simulations (BL_ID - BL_D) 
       
   b. Fig_GEMM_NCD_LRI_BL_ID_BL_I (Figure 4b)
       # Global distribution of mortality (GEMM NCD+LRI) associated with ship-related PM2.5, due to emissions from domestic vessels
       # calculated by mortality difference between two simulations (BL_ID - BL_I) 

   c. Fig_GEMM_NCD_LRI_BL_ID_S1N0_ID (Figure 5a)
       # Avoided Premature Deaths (NCD+LRI) associated with ship-related PM2.5 due to 0.5% Sulphur Cap
       # calculated by mortality difference between two simulations (BL_ID - S1N0_ID) 

   d. Fig_GEMM_NCD_LRI_S1N0_ID_S2N0_ID (Figure 5b)
       # Avoided Premature Deaths (NCD+LRI) associated with ship-related PM2.5 due to 0.1% Sulphur Cap
       # calculated by mortality difference between two simulations (S1N0_ID - S2N0_ID) 

   c. Fig_GEMM_NCD_LRI_S1N0_ID_S1N1_ID (Figure 5c)
       # Avoided Premature Deaths (NCD+LRI) associated with ship-related PM2.5 due to Tier III NOx Standard
       # calculated by mortality difference between two simulations (S1N0_ID - S1N1_ID) 


4. Fig_PM_GC_OBS_%location (eps/svg/png/pdf)
   # Figure S-2
   
   a. Fig_PM_GC_OBS_CN
       # Comparison of annual-average PM2.5 concentration between simulated results and observational data (China)
       # spatial map
       # corelation chart
   
   b. Fig_PM_GC_OBS_EU
       # Comparison of annual-average PM2.5 concentration between simulated results and observational data (Europe)
       # spatial map
       # corelation chart
   

