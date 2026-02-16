import { TRIPLYDB_ENDPOINT, ONTOLOGY_PREFIX } from '$env/static/private';


export interface SparqlBinding {
    type: string;
    value: string;
}

export interface SparqlResult {
    head: {
        vars: string[];
    };
    results: {
        bindings: Record<string, SparqlBinding>[];
    };
}

export async function executeSparqlQuery(query: string): Promise<SparqlResult> {
    console.log("Triply db", TRIPLYDB_ENDPOINT, ONTOLOGY_PREFIX)
    const response = await fetch(TRIPLYDB_ENDPOINT, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/sparql-query',
            'Accept': 'application/sparql-results+json'
        },
        body: query
    });

    if (!response.ok) {
        throw new Error(`SPARQL query failed: ${response.status} ${response.statusText}`);
    }

    console.log('SPARQL query executed successfully');
    return response.json();
}

export const SPARQL_PREFIXES = `
PREFIX : <${ONTOLOGY_PREFIX}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
`;
