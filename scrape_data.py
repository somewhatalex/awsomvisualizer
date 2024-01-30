from cdasws import CdasWs
cdas = CdasWs()
import warnings

# pip install -u xarray cdflib cdasws

cachedData = dict()

def scrapeData(vars, startTime, endTime):
    """
    REQUIRES:
    - vars: array with variables to collect
    - startTime, endTime: timeframe for which to return data

    EFFECTS: returns a formatted dict with scraped data from CDAS OMNI solar wind hourly average observations
    
    Accessing returned data:
    - data["variable"]["data"]
    - data["variable"]["timestamps"]
    """
    # if an identical request was previously made and cached, return that instead of waiting to make a new request
    cacheKey = (tuple(vars), startTime, endTime)
    if cacheKey in cachedData:
        return cachedData[cacheKey]
    
    # otherwise, proceed with scraping new data...

    # we can hide the "UserWarning" generated by the time to nanosecond conversion issue as pandas
    # now supports non-nanosecond time precision, so this is no longer an issue and should be ignored
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning)

        status, data = cdas.get_data("OMNI_COHO1HR_MERGED_MAG_PLASMA", vars, startTime, endTime)

        # check for errors when fetching data
        statusCode = status['http']['status_code']
        if(statusCode != 200):
            raise ConnectionError(f"Failed to connect to dataset. Status code: {statusCode}")
        
        print(f"Successfully scraped CDAS data. Status code: {statusCode}")

        # loop through and format scraped data into scrapedData
        scrapedData = dict()
        for var in vars:
            scrapedData[var] = {
                "data": data[var].values,
                "timestamps": data['Epoch'].values
            }

        # cache the newly scraped data
        cachedData[cacheKey] = scrapedData
        
        return scrapedData