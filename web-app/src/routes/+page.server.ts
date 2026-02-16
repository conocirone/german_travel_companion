import type { PageServerLoad } from './$types';
import { executeSparqlQuery, SPARQL_PREFIXES, ONTOLOGY_PREFIX } from '$lib/sparql';
import { BUDGET_OPTIONS, LOCATION_SETTING_OPTIONS, DAY_OPTIONS, type City } from '$lib/types';

async function fetchCities(): Promise<City[]> {
	const query = `${SPARQL_PREFIXES}
SELECT DISTINCT ?city WHERE {
  ?city a :City .
}
ORDER BY ?city
`;

	try {
		const result = await executeSparqlQuery(query);
		return result.results.bindings.map((binding) => {
			const uri = binding.city.value;
			// Extract city name from URI like "http://...#city_berlin" -> "berlin"
			const name = uri.replace(`${ONTOLOGY_PREFIX}city_`, '');
			// Capitalize first letter for display
			const displayName = name.charAt(0).toUpperCase() + name.slice(1);
			return { uri, name, displayName };
		});
	} catch (error) {
		console.error('Failed to fetch cities:', error);
		return [];
	}
}

export const load: PageServerLoad = async () => {
	const cities = await fetchCities();

	return {
		cities,
		budgetOptions: BUDGET_OPTIONS,
		locationSettingOptions: LOCATION_SETTING_OPTIONS,
		dayOptions: DAY_OPTIONS
	};
};
