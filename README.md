# ArangoDB Datasets

Package for loading pre-configured Graph datasets into an ArangoDB Instance.

**Installation**
```
pip install arango-datasets
```

**Usage**
```python
from arango import ArangoClient
from arango_datasets import Datasets

# Connect to database
db = ArangoClient(hosts=...).db(username=..., password=..., verify=True)

# Connect to datasets
datasets = Datasets(db)

# List datasets
print(datasets.list_datasets())

# List more information about a particular dataset
print(datasets.dataset_info("FLIGHTS")

# Load a dataset
datasets.load("FLIGHTS")
```


### Notable Datasets

#### Synthea P100

Synthea is an open-source synthetic patient dataset that simulates health records for a diverse set of fictional individuals. It includes demographic, clinical, and social data such as diagnoses, medications, procedures, and encounters over a patient’s lifetime. The data is generated using realistic patterns derived from real-world healthcare statistics, enabling its use in research, development, and testing of health IT systems while preserving patient privacy.

Source: https://synthea.mitre.org/

Size: 145514 nodes, 311701 edges

```python
print(datasets.dataset_info("SYNTHEA_P100"))

datasets.load("SYNTHEA_P100")
```

#### Common Vulnerability Exposures

This dataset contains information on Common Vulnerabilities and Exposures (CVE), providing details on known security vulnerabilities in software and hardware. It includes fields such as CVE ID, descriptions, severity scores (CVSS), affected products, and references. The dataset is useful for cybersecurity research, threat analysis, and vulnerability management, helping organizations track and mitigate security risks.

Source: https://www.kaggle.com/datasets/andrewkronser/cve-common-vulnerabilities-and-exposures

Size: 145506 nodes, 316967 edges

```python
print(datasets.dataset_info("CVE"))

datasets.load("CVE")
```

#### Flights

The Flights dataset in contains flight-related data, including information on routes, airports, and airlines. It is structured as a graph dataset, where airports act as nodes and flights between them as edges. This dataset is useful for demonstrating graph queries, shortest path analysis, and network connectivity.

Source: https://github.com/arangodb/example-datasets/tree/master/Data%20Loader

Size: 3375 nodes, 286463 edges

```python
print(datasets.dataset_info("FLIGHTS"))

datasets.load("FLIGHTS")
```

#### GDELT Open Intelligence

The GDELT Project (Global Database of Events, Language, and Tone) is an open dataset that monitors global news media in real-time. It captures and analyzes events, themes, emotions, and relationships across countries, organizations, and people. Covering millions of articles from various sources, GDELT provides insights into geopolitical trends, conflicts, and societal changes. The dataset is widely used in research, journalism, and AI applications for tracking global events and sentiment analysis.

Source: https://www.gdeltproject.org/

Size: 80047 nodes, 321819 edges

```python
print(datasets.dataset_info("OPEN_INTELLIGENCE"))

datasets.load("OPEN_INTELLIGENCE")
```

