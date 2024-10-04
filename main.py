from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
# or: requests.get(url).content
import geopandas as gpd
# import pandas as pd
import fiona
from pathlib import Path
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
print(dir_path)
fiona.supported_drivers['KML'] = 'rw'


# main function to transform shp to kml
def shp_to_kml(input_path, output_path):
    shpfileread = gpd.read_file(input_path)
    # fiona.supported_drivers['KML'] = 'rw'
    shpfileread.to_file(output_path, driver='KML')
    return "success"


# lädt kreise, gemeinden, gemarkungen und fluren
meta_url = 'https://www.laiv-mv.de/static/LAIV/Abt3.Geoinformation/Dateien/' \
           'DFG_MV.zip?ssoid=9c0981a1e910059742d37b27b58fc202'

extraction_path = './flurstuecke_mecklenburg/obere Verwaltungseinheiten/'

resp = urlopen(meta_url)
metazip = ZipFile(BytesIO(resp.read()))
for each_file in metazip.namelist():
    if not each_file.endswith('.zip'):  # optional filtering by filetype
        continue
    else:
        metazip.extract(each_file, path=extraction_path)
        zweite_zip = ZipFile(extraction_path + each_file)  # ./flurs../obere Verwal../2024-3.Q.zip beispielsweise
        zweite_zip.extractall(extraction_path)

pathlist = Path(dir_path).glob('*/obere Verwaltungseinheiten/*.shp')  # only .shp-files
for path in pathlist:
    # because path is object not string
    shp_path = str(path)
    kml_path = shp_path.replace('.shp', '.kml')
    job = shp_to_kml(shp_path, kml_path)
    # print(job)


shp_path = extraction_path + 'Gemarkungen.shp'

obere_verwaltungseinheiten = gpd.read_file(shp_path)

gemarkungen_array = obere_verwaltungseinheiten['ID_GMK'].to_list()

gemarkungen_array = [str(r) for r in gemarkungen_array]
# print(gemarkungen_array)

gemarkungen = gemarkungen_array

# lädt die flurstücke
for gemarkung in gemarkungen:
    gemarkung_id = gemarkung
    gemarkung_folder = f"./flurstuecke_mecklenburg/{gemarkung_id}/"

    url = f"https://www.geodaten-mv.de/dienste/alkis_wfs_einfach?SERVICE=wfs&VERSION=2.0.0&REQUEST=GetFeature&CRS=" \
          f"urn%3Aogc%3Adef%3Acrs%3AEPSG%3A%3A25833&OUTPUTFORMAT=application%2Fx-zip-shapefile&STOREDQUERY_ID=http%3A" \
          f"%2F%2Frepository.gdi-de.org%2Fquery%2Fadv%2Fprodukt%2Falkis-vereinfacht%2F2.0%2Fflst-by-gemarkung&" \
          f"GEMARKUNGSNUMMER={gemarkung_id}&id=418&ssoid=9c0981a1e910059742d37b27b58fc202"

    # print(url)
    resp = urlopen(url)
    myzip = ZipFile(BytesIO(resp.read()))
    # print(myzip.namelist())
    myzip.extractall(path=gemarkung_folder)

    shapefile_path = gemarkung_folder + 'ALKIS-Vereinfacht/Flurstueck.shp'
    # print(shapefile_path)

    # pd.set_option('display.max_rows', 500)
    # pd.set_option('display.max_columns', 500)

    kmlfile_path = gemarkung_folder + f"{gemarkung_id}.kml"
    job = shp_to_kml(shapefile_path, kmlfile_path)   # main-function
