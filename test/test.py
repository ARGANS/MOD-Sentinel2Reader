from s2reader import L2AProduct

# Initialise the SAFE product.
L2A_PROD = L2AProduct(".ignore/samples/S2A_MSIL2A_20230926T022331_N0509_R103_T51PUP_20230926T062553.SAFE/",
                     target_resolution=10)

# Access Metadata
L2A_PROD.meta.product    # ./MTD_MSIL2A.xml
L2A_PROD.meta.tile       # ./GRANULE/<TILE>/MTD_TL.xml
L2A_PROD.meta.bands      # Spectral Band Information (from metadata)

# Access the raster datacube (as xr.DataArray)
L2A_PROD.da

# Access the vector dataframe for footprint etc. (as gpd.GeoDataFrame)
L2A_PROD.da

# Read in B01, B02, Scene Classification and Water Vapour bands in a single xr.DataArray
L2A_PROD.read('B01', 'B02', 'WVP', 'SCL')