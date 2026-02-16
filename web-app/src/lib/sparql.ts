import { TRIPLYDB_ENDPOINT, ONTOLOGY_PREFIX } from '$env/static/private';
import type { Activity, ActivityType } from './types';

export { ONTOLOGY_PREFIX };

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

export interface SearchParams {
    city: string;
    day?: string;
    hour?: string;
    locationSetting?: string;
    budget?: string;
}

function sanitizeForUri(value: string): string {
    return value.toLowerCase().replace(/[^a-z0-9_]/g, '_');
}

function buildFilters(params: SearchParams): string {
    const filters: string[] = [];
    
    // City filter (required)
    filters.push(`?activity :isInCity :city_${sanitizeForUri(params.city)} .`);
    
    // Optional budget filter
    if (params.budget) {
        filters.push(`?activity :hasBudget :${params.budget} .`);
    }
    
    // Optional location setting filter
    if (params.locationSetting) {
        filters.push(`?activity :hasLocationSetting :${params.locationSetting} .`);
    }
    
    // Optional day and hour filter (only applies to PhysicalVenues with operating hours)
    if (params.day && params.hour) {
        filters.push(`
    OPTIONAL {
        ?activity :hasOperatingHours ?hours .
        ?hours :appliesToDay :day_${params.day} .
        ?hours :opensAt ?opensAt .
        ?hours :closesAt ?closesAt .
    }
    FILTER(
        !BOUND(?hours) ||
        (?opensAt <= "${params.hour}" && "${params.hour}" < ?closesAt)
    )`);
    } else if (params.day) {
        filters.push(`
    OPTIONAL {
        ?activity :hasOperatingHours ?hours .
        ?hours :appliesToDay :day_${params.day} .
    }
    FILTER(!BOUND(?hours) || BOUND(?hours))`);
    }
    
    return filters.join('\n    ');
}

export function buildActivitySearchQuery(params: SearchParams, limit?: number, offset?: number): string {
    const filters = buildFilters(params);

    let paginationClause = '';
    if (limit !== undefined) {
        paginationClause = `\nLIMIT ${limit}`;
        if (offset !== undefined && offset > 0) {
            paginationClause += `\nOFFSET ${offset}`;
        }
    }
    
    return `${SPARQL_PREFIXES}
SELECT DISTINCT ?activity ?activityType ?budget ?locationSetting ?imageUrl ?url ?duration ?languages ?meetingPointDesc WHERE {
    ?activity rdf:type ?activityType .
    ?activityType rdfs:subClassOf* :Activity .
    FILTER(?activityType != :Activity && ?activityType != :PhysicalVenue)
    
    ${filters}
    
    OPTIONAL { ?activity :hasBudget ?budget }
    OPTIONAL { ?activity :hasLocationSetting ?locationSetting }
    OPTIONAL { ?activity :hasImageURL ?imageUrl }
    OPTIONAL { ?activity :hasURL ?url }
    OPTIONAL { ?activity :hasDuration ?durationObj . ?durationObj rdfs:label ?duration }
    OPTIONAL { ?activity :hasLanguage ?langObj . ?langObj rdfs:label ?languages }
    OPTIONAL { ?activity :hasMeetingPoint ?meetingPointObj . ?meetingPointObj :hasMeetingPointDescription ?meetingPointDesc }
}
ORDER BY ?activity${paginationClause}
`;
}

export function buildActivityCountQuery(params: SearchParams): string {
    const filters = buildFilters(params);
    
    return `${SPARQL_PREFIXES}
SELECT (COUNT(DISTINCT ?activity) AS ?count) WHERE {
    ?activity rdf:type ?activityType .
    ?activityType rdfs:subClassOf* :Activity .
    FILTER(?activityType != :Activity && ?activityType != :PhysicalVenue)
    
    ${filters}
}
`;
}

function extractLocalName(uri: string): string {
    const hashIndex = uri.lastIndexOf('#');
    const slashIndex = uri.lastIndexOf('/');
    const index = Math.max(hashIndex, slashIndex);
    return index >= 0 ? uri.substring(index + 1) : uri;
}

function formatActivityName(uri: string): string {
    const localName = extractLocalName(uri);
    // Remove prefixes like "tour_", "museum_", "park_", "sight_", "nightlifevenue_"
    const namePart = localName.replace(/^(tour|museum|park|sight|nightlifevenue)_/i, '');
    // Replace underscores with spaces and convert to title case
    return namePart
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase());
}

function determineActivityType(typeUri: string): ActivityType {
    const localName = extractLocalName(typeUri).toLowerCase();
    if (localName === 'tour') return 'Tour';
    if (localName === 'museum') return 'Museum';
    if (localName === 'park') return 'Park';
    if (localName === 'sight') return 'Sight';
    if (localName === 'nightlifevenue') return 'NightlifeVenue';
    return 'Sight'; // Default fallback
}

function formatBudget(budgetUri?: string): string | undefined {
    if (!budgetUri) return undefined;
    const localName = extractLocalName(budgetUri);
    return localName.replace('budget_', '');
}

function formatLocationSetting(settingUri?: string): string | undefined {
    if (!settingUri) return undefined;
    const localName = extractLocalName(settingUri);
    return localName.replace('location_', '');
}

function extractCity(activityUri: string, params: SearchParams): string {
    // Use the city from search params since we filter by it
    return params.city.charAt(0).toUpperCase() + params.city.slice(1);
}

export function parseActivityResults(bindings: Record<string, SparqlBinding>[], params: SearchParams): Activity[] {
    return bindings.map((binding) => ({
        uri: binding.activity.value,
        name: formatActivityName(binding.activity.value),
        type: determineActivityType(binding.activityType.value),
        city: extractCity(binding.activity.value, params),
        budget: formatBudget(binding.budget?.value),
        locationSetting: formatLocationSetting(binding.locationSetting?.value),
        imageUrl: binding.imageUrl?.value,
        url: binding.url?.value,
        duration: binding.duration?.value,
        languages: binding.languages?.value,
        meetingPoint: binding.meetingPointDesc?.value
    }));
}
