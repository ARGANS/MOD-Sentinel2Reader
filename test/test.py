from s2reader import L2AProduct

# Initialise the SAFE product.
product = L2AProduct(".ignore/samples/S2A_MSIL2A_20230926T022331_N0509_R103_T51PUP_20230926T062553.SAFE",
                     target_resolution=20)

# Read in the 10m VNIR and SCL
product.read('SCL','B02','B03','B04', 'B08')