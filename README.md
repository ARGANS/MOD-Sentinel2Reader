# MOD-Sentinel2Reader

A module to read `Sentinel 2` `L1C` and `L2A` products, providing an interface to the data with typical pre-processing steps applied to the dataset. Data is stored and exposed in common and flexible datatypes in `xarray.DataArray` (with `rioxarray` ), and `geopandas.GeoDataFrame`.
  
**Developed for use in CopPhil for GeoVille Docker Containers, where raw `.SAFE` products are mounted within `/eodata`.**

---

### **Features**
- **Reflectance Bands**
- **Define Masks** (based on other bands e.g. SCL)
- **Atmospheric Bands** (e.g., AOT, WVP)
- **Scene Classification**
- **Product and Tile Metadata**
- **Geometries** (e.g., VZA, VAA, SZA, SAA) *(In Progress)*
- **Detector Footprints** *(In Progress)*
- **Quality Bands** *(In Progress)*
- **Data Footprint** *(In Progress)*

---

### **Example**

The following example demonstrates how a user can interact with the `.SAFE` folder to connect to the product, read reflectance bands with differing resolutions, as well as non-reflectance bands requiring different pre-processing steps (e.g., reflectance bands need offset and quantification values, whereas atmospheric bands only require quantification).

```python
from s2reader import L2AProduct

# Initialize the SAFE product.
L2A_PROD = L2AProduct(
    ".ignore/samples/S2A_MSIL2A_20230926T022331_N0509_R103_T51PUP_20230926T062553.SAFE/",
    target_resolution=20,
    mask={'SCL': [0.0, 3.0, 8.0, 9.0]}  # Define mask using SCL layer and NoData/Cloud related values.
)

# Access Metadata
L2A_PROD.meta.product    # ./MTD_MSIL2A.xml
L2A_PROD.meta.tile       # ./GRANULE/<TILE>/MTD_TL.xml
L2A_PROD.meta.bands      # Spectral Band Information (from metadata)

# Access the raster data (as xr.DataArray)
L2A_PROD.da

# Access the vector data (as gpd.GeoDataFrame)
L2A_PROD.gdf

# Read in B01, B02, Scene Classification, and Water Vapour bands in a single xr.DataArray, masked to the SCL
L2A_PROD.read('B01', 'B02', 'WVP', 'SCL')
L2A_PROD.da.rio.to_raster('S2-READER-EXAMPLE.tif')
```

### **Installation (TBC)**
#### 1. **Using `uv` (Recommended)**
```bash
uv pip install .
```
#### 2. **Using `pip`**
```bash
pip install .
```