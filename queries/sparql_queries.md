
## Query 1: Which outdoor activities in Berlin have a "Free" budget?

**Competency Question:** Which outdoor activities in Berlin have a "Free" budget?

```sparql
PREFIX : <http://www.semanticweb.org/german_tourism_activities#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?activity ?activityType
WHERE {
  # Find all activities
  ?activity rdf:type ?activityType .
  ?activityType rdfs:subClassOf* :Activity .
  
  # Must be in Berlin
  ?activity :isInCity ?city .
  FILTER(CONTAINS(LCASE(STR(?city)), "berlin"))
  
  # Must have outdoor location setting
  ?activity :hasLocationSetting ?locationSetting .
  FILTER(CONTAINS(LCASE(STR(?locationSetting)), "outdoor"))
  
  # Must have free budget
  ?activity :hasBudget ?budget .
  FILTER(CONTAINS(LCASE(STR(?budget)), "free"))
}
ORDER BY ?activity
```

**Expected Results:** List of tours and venues in Berlin that are outdoor and free.

---

## Query 2: Is there any Museum in Munich that operates on Sundays?

**Competency Question:** Is there any Museum in Munich that operates on Sundays?

**Boolean Version (Yes/No answer):**
```sparql
PREFIX : <http://www.semanticweb.org/german_tourism_activities#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

ASK {
  ?museum rdf:type :Museum .
  ?museum :isInCity ?city .
  FILTER(CONTAINS(LCASE(STR(?city)), "munich"))
  ?museum :hasOperatingHours ?hours .
  ?hours :appliesToDay ?day .
  FILTER(CONTAINS(LCASE(STR(?day)), "sunday"))
}
```

---

## Query 3: What is the category of the "Mercedes-Benz Museum"?

**Competency Question:** What is the category of the "Mercedes-Benz Museum"?

```sparql
PREFIX : <http://www.semanticweb.org/german_tourism_activities#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?museum ?museumType
WHERE {
  # Find the Mercedes-Benz Museum
  ?museum rdf:type :Museum .
  FILTER(CONTAINS(LCASE(STR(?museum)), "mercedes"))
  
  # Get its museum type/category
  ?museum :hasMuseumType ?museumType .
}
```

**Expected Results:** The museum type/category of Mercedes-Benz Museum.

---

## Query 4: How many indoor Nightlife Venues in Hamburg have a "Medium" budget?

**Competency Question:** How many indoor Nightlife Venues in Hamburg have a "Medium" budget?

```sparql
PREFIX : <http://www.semanticweb.org/german_tourism_activities#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT (COUNT(?venue) AS ?count)
WHERE {
  # Must be a Nightlife Venue
  ?venue rdf:type :NightlifeVenue .
  
  # Must be in Hamburg
  ?venue :isInCity ?city .
  FILTER(CONTAINS(LCASE(STR(?city)), "hamburg"))
  
  # Must be indoor
  ?venue :hasLocationSetting ?locationSetting .
  FILTER(CONTAINS(LCASE(STR(?locationSetting)), "indoor"))
  
  # Must have medium budget
  ?venue :hasBudget ?budget .
  FILTER(CONTAINS(LCASE(STR(?budget)), "medium"))
}
```

**Expected Results:** A count of matching nightlife venues.

---

## Query 5: Which park in Hamburg close after 18:00?

**Competency Question:** Which park in Hamburg close after 18:00?

```sparql
PREFIX : <http://www.semanticweb.org/german_tourism_activities#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?park ?closingTime
WHERE {
  # Must be a Park
  ?park rdf:type :Park .
  
  # Must be in Hamburg
  ?park :isInCity ?city .
  FILTER(CONTAINS(LCASE(STR(?city)), "hamburg"))
  
  # Get operating hours and closing time
  ?park :hasOperatingHours ?hours .
  ?hours :closesAt ?closingTime .
  
  # Filter for closing times after 18:00 (string comparison works for HH:MM format)
  FILTER(?closingTime > "18:00")
}
ORDER BY ?closingTime
```

**Expected Results:** Parks in Hamburg that close after 6:00 PM with their closing times.

---

## Query 6: What is the duration of the guided tour "Old Town Walk"?

**Competency Question:** What is the duration of the guided tour "Old Town Walk"?

```sparql
PREFIX : <http://www.semanticweb.org/german_tourism_activities#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?tour ?duration
WHERE {
  ?tour rdf:type :Tour .
  FILTER(CONTAINS(LCASE(STR(?tour)), "old") && CONTAINS(LCASE(STR(?tour)), "town"))
  ?tour :hasDuration ?duration .
}
```

**Expected Results:** The duration object/value for the Old Town Walk tour.

