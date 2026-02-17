import { TRIPLYDB_ENDPOINT, ONTOLOGY_PREFIX } from '$env/static/private';
import type { Activity, ActivityType } from './types';

export { ONTOLOGY_PREFIX };

/**
 * Represents a single value returned from a SPARQL result set.
 * Every SPARQL variable binding has a `type` (e.g. "uri", "literal") and its string `value`.
 */
export interface SparqlBinding {
    type: string;
    value: string;
}

/**
 * The JSON structure returned by a SPARQL endpoint when using
 * `Accept: application/sparql-results+json`.
 *
 * - `head.vars` — the list of projected variable names from the SELECT clause.
 * - `results.bindings` — an array of solution rows, each being a map from
 *   variable name to its {@link SparqlBinding}.
 */
export interface SparqlResult {
    head: {
        vars: string[];
    };
    results: {
        bindings: Record<string, SparqlBinding>[];
    };
}

/**
 * Sends a SPARQL query to the TriplyDB endpoint via HTTP POST and returns
 * the parsed JSON result.
 *
 * The request uses:
 * - `Content-Type: application/sparql-query` — tells the endpoint the body is raw SPARQL.
 * - `Accept: application/sparql-results+json` — requests JSON-formatted results.
 *
 * @param query - A complete SPARQL query string (including prefixes).
 * @returns The parsed {@link SparqlResult} containing variable bindings.
 * @throws If the HTTP response status is not OK.
 */
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

/**
 * Standard SPARQL prefix declarations prepended to every query.
 *
 * - `:` — the project's own ontology namespace (e.g. classes like `:Tour`, properties
 *   like `:isInCity`, individuals like `:city_berlin`). Set via the `ONTOLOGY_PREFIX` env var.
 * - `rdf:` — RDF vocabulary. Used for `rdf:type` to determine what class an individual belongs to.
 * - `rdfs:` — RDF Schema. Used for `rdfs:subClassOf` (class hierarchy traversal)
 *   and `rdfs:label` (human-readable names for auxiliary nodes like Duration).
 * - `xsd:` — XML Schema Datatypes. Available for typed literals (e.g. time strings).
 */
export const SPARQL_PREFIXES = `
PREFIX : <${ONTOLOGY_PREFIX}>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
`;

/**
 * User-supplied search criteria that drive dynamic SPARQL filter generation.
 *
 * - `city` (required) — the city local name (e.g. "berlin"). Used to match `:city_berlin`.
 * - `day` (optional) — weekday name (e.g. "monday"). Used to filter by operating hours.
 * - `hour` (optional) — time string in HH:MM format (e.g. "14:00"). Combined with `day`
 *   to check that an activity is open at that specific time.
 * - `locationSetting` (optional) — e.g. "location_indoor" or "location_outdoor".
 * - `budget` (optional) — e.g. "budget_free", "budget_low", "budget_medium", "budget_high".
 */
export interface SearchParams {
    city: string;
    day?: string;
    hour?: string;
    locationSetting?: string;
    budget?: string;
}

/**
 * Converts a user-supplied string into a safe ontology URI local name.
 *
 * Ontology individuals use lowercase, underscore-separated names (e.g. "city_berlin").
 * This strips any character that isn't alphanumeric or underscore to prevent
 * SPARQL injection and URI malformation.
 *
 * @param value - Raw user input (e.g. a city name).
 * @returns A sanitized string safe for interpolation into a SPARQL `:prefix_name` URI.
 */
function sanitizeForUri(value: string): string {
    return value.toLowerCase().replace(/[^a-z0-9_]/g, '_');
}

/**
 * Builds the dynamic triple-pattern and FILTER clauses injected into the WHERE
 * block of the SPARQL query, based on the user's search criteria.
 *
 * The generated patterns serve different roles:
 *
 * ### 1. City filter (always added)
 * ```sparql
 * ?activity :isInCity :city_berlin .
 * ```
 * A required triple pattern that restricts results to activities linked to the
 * selected city individual. The city name is sanitized via {@link sanitizeForUri}
 * and prefixed with `city_` to match the ontology naming convention.
 *
 * ### 2. Budget filter (added when `params.budget` is set)
 * ```sparql
 * ?activity :hasBudget :budget_low .
 * ```
 * A mandatory triple pattern (not OPTIONAL) that excludes activities whose budget
 * level doesn't match. The value (e.g. `budget_low`) maps directly to an ontology
 * individual URI.
 *
 * ### 3. Location setting filter (added when `params.locationSetting` is set)
 * ```sparql
 * ?activity :hasLocationSetting :location_outdoor .
 * ```
 * Same pattern as budget — a mandatory match against the location setting individual.
 *
 * ### 4. Day + Hour filter (added when temporal params are provided)
 *
 * **When both `day` and `hour` are provided:**
 * ```sparql
 * OPTIONAL {
 *     ?activity :hasOperatingHours ?hours .
 *     ?hours :appliesToDay :day_monday .
 *     ?hours :opensAt ?opensAt .
 *     ?hours :closesAt ?closesAt .
 * }
 * FILTER(
 *     !BOUND(?hours) ||
 *     (?opensAt <= "14:00" && "14:00" < ?closesAt)
 * )
 * ```
 * This uses an **open-world assumption**: the OPTIONAL block tries to find operating
 * hours for the given day. The FILTER then applies two-branch logic:
 * - `!BOUND(?hours)` — if the activity has **no operating hours at all** (e.g. a Tour
 *   that doesn't publish hours), it is **included** rather than excluded. Missing data
 *   does not imply "closed".
 * - If hours **are** bound, the requested time must fall within the `[opensAt, closesAt)`
 *   interval (inclusive open, exclusive close).
 *
 * **When only `day` is provided (no hour):**
 * A permissive OPTIONAL + FILTER that effectively includes all activities regardless
 * of whether they have hours for that day. This ensures no activities are wrongly
 * excluded when the user hasn't specified a time.
 *
 * @param params - The user's search criteria.
 * @returns A string of SPARQL triple patterns and FILTERs to be interpolated
 *          into the WHERE clause.
 */
function buildFilters(params: SearchParams): string {
    const filters: string[] = [];
    
    // City filter (required) — matches the activity to the selected city individual
    filters.push(`?activity :isInCity :city_${sanitizeForUri(params.city)} .`);
    
    // Budget filter — mandatory match, excludes activities with a different budget level
    if (params.budget) {
        filters.push(`?activity :hasBudget :${params.budget} .`);
    }
    
    // Location setting filter — mandatory match against indoor/outdoor individual
    if (params.locationSetting) {
        filters.push(`?activity :hasLocationSetting :${params.locationSetting} .`);
    }
    
    // Temporal filter — uses OPTIONAL + FILTER for open-world reasoning:
    // activities without operating hours data are still included (not penalized
    // for missing information), while those WITH hours must satisfy the time check.
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
        // Day-only: permissive filter, it includes activities whether or not they have hours for the selected day
        filters.push(`
    OPTIONAL {
        ?activity :hasOperatingHours ?hours .
        ?hours :appliesToDay :day_${params.day} .
    }
    FILTER(!BOUND(?hours) || BOUND(?hours))`);
    }
    
    return filters.join('\n    ');
}

/**
 * Builds a complete SPARQL SELECT query to retrieve activities matching the
 * user's search criteria, along with all their display metadata.
 *
 * The query is structured in layers:
 *
 * ### Static core — class hierarchy traversal
 * ```sparql
 * ?activity rdf:type ?activityType .
 * ?activityType rdfs:subClassOf* :Activity .
 * FILTER(?activityType != :Activity && ?activityType != :PhysicalVenue)
 * ```
 * - `rdf:type` binds each activity to its specific class (Tour, Museum, Park, etc.).
 * - `rdfs:subClassOf*` uses the **transitive closure** operator (`*`) to walk the
 *   class hierarchy upward. This matches any class that is `:Activity` itself or a
 *   subclass at any depth, making the query resilient to future ontology changes
 *   (e.g. adding a new subclass of PhysicalVenue).
 * - The `FILTER` excludes the abstract superclasses `:Activity` and `:PhysicalVenue`
 *   so only concrete leaf types are returned.
 *
 * ### Dynamic filters (from {@link buildFilters})
 * Injected triple patterns and FILTERs for city, budget, location setting, and
 * temporal availability. See {@link buildFilters} for detailed documentation.
 *
 * ### OPTIONAL metadata block
 * ```sparql
 * OPTIONAL { ?activity :hasBudget ?budget }
 * OPTIONAL { ?activity :hasImageURL ?imageUrl }
 * OPTIONAL { ?activity :hasDuration ?durationObj . ?durationObj rdfs:label ?duration }
 * ...
 * ```
 * Each OPTIONAL fetches a display property. Using OPTIONAL ensures activities are
 * still returned even if they lack some metadata (e.g. no image, no duration).
 * Properties like duration, language, and meeting point use an extra join through
 * an intermediate node (e.g. a Duration individual) and extract the human-readable
 * label via `rdfs:label` or a description property.
 *
 * ### SELECT DISTINCT
 * Eliminates duplicate rows that can arise when an activity has multiple values
 * for an optional property (e.g. multiple languages).
 *
 * ### ORDER BY + pagination
 * Results are ordered alphabetically by activity URI for stable ordering.
 * Optional LIMIT/OFFSET clauses enable server-side pagination (currently unused
 * as pagination is handled client-side).
 *
 * @param params - The user's search criteria.
 * @param limit - Optional maximum number of results to return.
 * @param offset - Optional number of results to skip (for pagination).
 * @returns A complete SPARQL query string ready to be sent to the endpoint.
 */
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

/**
 * Builds a SPARQL query that counts matching activities without fetching their
 * metadata. Uses the same static core and dynamic filters as
 * {@link buildActivitySearchQuery} but projects only `COUNT(DISTINCT ?activity)`.
 *
 * Used for pagination to determine the total number of results
 * without transferring all the data.
 *
 * @param params - The user's search criteria.
 * @returns A SPARQL query string that returns a single `?count` binding.
 */
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

/**
 * Extracts the local name (fragment) from a full URI.
 *
 * Ontology URIs may use either `#` or `/` as the namespace separator:
 * - `http://example.org/ontology#Tour` → `Tour`
 * - `http://example.org/ontology/tour_berlin_walking` → `tour_berlin_walking`
 *
 * Takes the part after whichever separator (`#` or `/`) appears last.
 *
 * @param uri - A full RDF resource URI.
 * @returns The local name portion after the last `#` or `/`.
 */
function extractLocalName(uri: string): string {
    const hashIndex = uri.lastIndexOf('#');
    const slashIndex = uri.lastIndexOf('/');
    const index = Math.max(hashIndex, slashIndex);
    return index >= 0 ? uri.substring(index + 1) : uri;
}

/**
 * Converts an activity URI into a human-readable display name.
 *
 * Ontology activity URIs follow the pattern `{type}_{descriptive_name}`, e.g.:
 * - `tour_berlin_walking_tour` → "Berlin Walking Tour"
 * - `museum_pergamon` → "Pergamon"
 *
 * Steps:
 * 1. Extract the local name from the URI via {@link extractLocalName}.
 * 2. Strip the type prefix (`tour_`, `museum_`, `park_`, `sight_`, `nightlifevenue_`).
 * 3. Replace underscores with spaces.
 * 4. Title-case each word.
 *
 * @param uri - The full URI of an activity individual.
 * @returns A formatted, title-cased display name.
 */
function formatActivityName(uri: string): string {
    const localName = extractLocalName(uri);
    // Remove prefixes like "tour_", "museum_", "park_", "sight_", "nightlifevenue_"
    const namePart = localName.replace(/^(tour|museum|park|sight|nightlifevenue)_/i, '');
    // Replace underscores with spaces and convert to title case
    return namePart
        .replace(/_/g, ' ')
        .replace(/\b\w/g, (c) => c.toUpperCase());
}

/**
 * Maps an `rdf:type` URI to the application's {@link ActivityType} union.
 *
 * The ontology defines concrete activity classes: Tour, Museum, Park, Sight,
 * NightlifeVenue. This function extracts the local name and maps it to the
 * corresponding TypeScript type. Falls back to `'Sight'` for any unrecognized
 * type, ensuring the UI always has a valid category to display.
 *
 * @param typeUri - The full URI of the RDF class (e.g. `:Tour`, `:Museum`).
 * @returns The matching {@link ActivityType} string literal.
 */
function determineActivityType(typeUri: string): ActivityType {
    const localName = extractLocalName(typeUri).toLowerCase();
    if (localName === 'tour') return 'Tour';
    if (localName === 'museum') return 'Museum';
    if (localName === 'park') return 'Park';
    if (localName === 'sight') return 'Sight';
    if (localName === 'nightlifevenue') return 'NightlifeVenue';
    return 'Sight'; // Default fallback
}

/**
 * Converts a budget individual URI (e.g. `:budget_low`) into a display string
 * by stripping the `budget_` prefix → `"low"`.
 *
 * @param budgetUri - The full URI of the budget individual, or undefined.
 * @returns The budget label (e.g. "free", "low", "medium", "high"), or undefined.
 */
function formatBudget(budgetUri?: string): string | undefined {
    if (!budgetUri) return undefined;
    const localName = extractLocalName(budgetUri);
    return localName.replace('budget_', '');
}

/**
 * Converts a location setting URI (e.g. `:location_outdoor`) into a display
 * string by stripping the `location_` prefix → `"outdoor"`.
 *
 * @param settingUri - The full URI of the location setting individual, or undefined.
 * @returns The setting label (e.g. "indoor", "outdoor"), or undefined.
 */
function formatLocationSetting(settingUri?: string): string | undefined {
    if (!settingUri) return undefined;
    const localName = extractLocalName(settingUri);
    return localName.replace('location_', '');
}

/**
 * Returns the display name for the city. Since all results are already filtered
 * to a single city via the SPARQL query, we can use the search parameter directly
 * rather than parsing it from each activity URI.
 *
 * @param activityUri - The activity URI (unused, kept for potential future use).
 * @param params - The search parameters containing the city name.
 * @returns The city name with the first letter capitalized.
 */
function extractCity(activityUri: string, params: SearchParams): string {
    return params.city.charAt(0).toUpperCase() + params.city.slice(1);
}

/**
 * Transforms raw SPARQL result bindings into typed {@link Activity} objects
 * suitable for rendering in the UI.
 *
 * Each binding row from the SPARQL result set contains URI values for the
 * projected variables. This function:
 * 1. Extracts and formats the activity name from its URI (via {@link formatActivityName}).
 * 2. Determines the concrete activity type from the `?activityType` URI (via {@link determineActivityType}).
 * 3. Formats budget and location setting URIs into display labels.
 * 4. Passes through optional string properties (imageUrl, url, duration, languages, meetingPoint)
 *    directly from the bindings, using `undefined` for any missing OPTIONAL values.
 *
 * @param bindings - The `results.bindings` array from a {@link SparqlResult}.
 * @param params - The original search parameters (used to derive the city name).
 * @returns An array of {@link Activity} objects ready for display.
 */
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
