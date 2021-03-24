# Predicting Emissions

This work is currently in progress. 


### Brief Outline

This repository contains an analysis of longitudinal (years 2017-2017) neighbourhood greenhouse gas emissions of UK households. The aim of the project is to use spatial-temporal methods to assess change of neighbourhoods' consumption-based emissions over time. This is done for total emissions as well as emissions by product types. 

### Background

It is important for the UK Government to be able to predict and understand greenhouse gas (GHG) emissions to meet climate change reduction targets. Yet, despite the UK reporting higher consumption- than production-based GHG emissions, frameworks to measure and mitigate production-based emissions continue to be better understood. While more recent research has begun looking at the UK’s consumption-based GHG emissions, household differences in consumption patterns are not yet well-understood. GHG footprints are linked to various demographic variables, where higher emissions are most frequently linked to higher income (e.g. Vringer and Blok, 1995; Wier et al., 2001; Lenzen et al., 2004; Druckman and Jackson, 2008; Minx et al., 2013). However, despite income being a good predictor of total emissions, we argue that a product-level approach considering a variety of spatial and socio-demographic variables is needed. The reasons for this are twofold: firstly, some research has linked higher incomes and expenditures to greener consumption and thus concluded that higher incomes do not per se determine higher emissions (Girod and de Haan, 2009; 2010), and secondly, differences in emissions between various products and services make it more urgent to reduce emissions in different sectors and should be linked to different reduction strategies for different sectors. Thus, using income as a proxy may overlook product-level differences. 

### Completed to date
Thus far emission estimates of UK neighbourhoods have been generated using the UKMRIO model in combination with the Living Costs and Food Survey (LCFS). In addition, socio-demographic variables have been extrated from the LCFS. 

Training in spatial-temporal analysis is undertaken and included in this repository. Web links for training resources are included in the training scripts.

### Next steps
The spatial-temporal analysis needs to be extended to product types. In addition, socio-demographic variables are needed to assess correlations between these and to construct models to predict product-level emissions, which are robust over time. 

### References
__Background__
- Druckman, A. and Jackson, T. 2008. Household energy consumption in the UK: A highly geographically and socio-economically disaggregated model. Energy Policy. 36(8), pp.3167–3182.
- Girod, B. and de Haan, P. 2009. GHG reduction potential of changes in consumption patterns and higher quality levels: Evidence from Swiss household consumption survey. Energy Policy. 37(12), pp.5650–5661.
- Girod, B. and de Haan, P. 2010. More or better? A model for changes in household greenhouse gas emissions due to higher income. Journal of Industrial Ecology. 14(1), pp.31–49.
- Lenzen, M., Dey, C. and Foran, B. 2004. Energy requirements of Sydney households. Ecological Economics. 49(3), pp.375–399.
- Minx, J.C., Baiocchi, G., Wiedmann, T.O., Barrett, J., Creutzig, F., Feng, K., Förster, M., Pichler, P.-P.P., Weisz, H. and Hubacek, K. 2013. Carbon footprints of cities and other human settlements in the UK. Environmental Research Letters. 8(3), pp.1–10.
- Vringer, K. and Blok, K. 1995. The direct and indirect energy requirements of households in the Netherlands. Energy Policy. 23(10), pp.893–910.
Wier, M., Lenzen, M., Munksgaard, J. and Smed, S. 2001. Effects of household consumption patterns on CO2 requirements. Economic Systems Research. 13(3), pp.259–274.



__Training Links__
- http://darribas.org/gds_scipy16/ipynb_md/05_spatial_dynamics.html
- https://pysal.org/notebooks/explore/giddy/Markov_Based_Methods.html
- https://pysal.org/notebooks/lib/libpysal/weights.html

