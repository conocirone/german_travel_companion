import type { Actions, PageServerLoad } from './$types';
import { ONTOLOGY_PREFIX } from '$env/static/private';
import { SPARQL_PREFIXES } from '$lib/sparql';
import { executeSparqlQuery } from '$lib/sparql';
import { BUDGET_OPTIONS, LOCATION_SETTING_OPTIONS, DAY_OPTIONS, type City } from '$lib/types';
import { searchFormSchema, type SearchFormErrors } from '$lib/validation';
import { fail } from '@sveltejs/kit';

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

export const actions: Actions = {
    search: async ({ request }) => {
        const formData = await request.formData();
        const rawData = {
            city: formData.get('city')?.toString(),
            day: formData.get('day')?.toString(),
            hour: formData.get('hour')?.toString(),
            locationSetting: formData.get('locationSetting')?.toString(),
            budget: formData.get('budget')?.toString()
        };

        const result = searchFormSchema.safeParse(rawData);

        if (!result.success) {
            const errors: SearchFormErrors = {};
            for (const issue of result.error.issues) {
                const field = issue.path[0] as keyof SearchFormErrors;
                if (!errors[field]) {
                    errors[field] = [];
                }
                errors[field]!.push(issue.message);
            }

            return fail(400, {
                errors,
                values: rawData
            });
        }

        // Form is valid - return the validated data
        // Query execution will be implemented in the next phase
        console.log('Valid search request:', result.data);

        return {
            success: true,
            searchParams: result.data
        };
    }
};
