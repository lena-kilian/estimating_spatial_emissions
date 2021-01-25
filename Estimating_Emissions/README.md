# Estimating Emissions

This folder contains scripts which generate emission estimates of UK neighbourhoods. These have been generated using the UKMRIO model in combination with the Living Costs and Food Survey (LCFS). In addition, socio-demographic variables have been extrated from the LCFS. 

Please note: _The code in this repository is incomplete and for reference only. Some scripts could not be uploaded currently as permission from all collaborators is needed first. Outputs of emission estimates will be uploaded to the University of Leeds' data repository in the future._

### File Descriptions

|File Name|Description|
|-|-|
|LCFS_aggregation.py|Groups LCFS observations by region and Output Area Classification. A minimum of 10 observations per group is ensured|
|LCFS_aggregation_functions.py|Contains functions needed for LCFS_aggregation.py|
|LCFS_make_coicop_dict.py|Generates lookup file for Coicop descriptions and LCFS variables|
|LCFS_PhysicalUnits_Flights.py|Generates a proxy variable for flights consumed, based on number of flights taken|
|LCFS_PhysicalUnits_Rent.py|Generates a proxy variable for emission distribution of UK emissions linked to rent, based on the number of rooms a household has access to|
|lcfsXoac_analysis.py|Generated grrenhouse gas emission estimates for UK OAs, LSOAs, and MSOAs|
