# Extract, Transform, (Aggregate), Load

These scripts take the following inputs:

  * permissions (__categorical data__)
  * domains  
  * metaDataNames (a.k.a. API Key names) (__categorical data__)
  * broadcastReceiverIntentFilterActionNames (__categorical data__) 
  * dependency (a.k.a names of the used libraries) (__categorical data__)

It will make bitvectors out of all the (__categorical data__) inputs.
And will make scalar (numerical) columns for the number of domains.

## Output

The output shall be a pandas Dataframe, as described in [the wiki](https://gitlab.com/trackingthetrackers/wiki/-/wikis/Pandas-internal-data-format-for-the-ML-part).

## ETL steps

The script will search these directories for .json files (which need to conform to [our JSON format](https://gitlab.com/trackingthetrackers/wiki/-/wikis/JSON-format-definition-for-feature-vectors):

  * ``data/XXX ``... for permissions
  * ``data/extracted-features/unzip-ipgrep`` ... for domains
  * ``data/extracted-features/axml-meta-data/names.json`` ... for metaDataNames
  * ``data/extracted-features/axml-meta-data/receivers.json`` ... for broadcastReceiverIntentFilterActionNames
  *	``data/extracted-features/XXX`` ... dependencies 

## Domains processing

The scripts will need two lists of domains: 
 - known tracking domains (obtained from advertising lists, adblockers, exodus )
 - known good domains: these are the Alexa-top-N (__N__ is 10000 for us) domains **minus** the known tracking domains

A domain from the domains input list will be compared against both lists, if it is in the known tracking list, it will increment the 
``nr_of_tracking_domains_found`` integer. Otherwise, if it is in the clean domain list, ``nr_of_clean_domains_found`` will be incremented.
If not, the ``nr_of_unknown_domains_found`` int will be incremented.

## Categorical data

All of the other categorical data types (permissions, metaDataNames, etc.) will be represented as a bitvector.


## Labels

For training data,  the dataframe will include a ``label`` which is 0 or 1 . 0 meaning clean, 1 meaning "contains trackers".
For inference (classification), this column will exist but contain ``n/a`` values.

# Loading the data

Via the function 

``python
def load_data():
   pass...
``

It will deal with loading the data and creating the dataframe.


