import type { Actions, PageServerLoad } from './$types';
import { SPARQL_PREFIXES, ONTOLOGY_PREFIX } from '$lib/sparql';
import { executeSparqlQuery, buildActivitySearchQuery, parseActivityResults } from '$lib/sparql';
import { BUDGET_OPTIONS, LOCATION_SETTING_OPTIONS, DAY_OPTIONS, type City, type Activity } from '$lib/types';
import { searchFormSchema } from '$lib/validation';
import { fail } from '@sveltejs/kit';
import { superValidate, setError } from 'sveltekit-superforms';
import { zod4 } from 'sveltekit-superforms/adapters';

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
			const name = uri.replace(`${ONTOLOGY_PREFIX}city_`, '');
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
	const form = await superValidate(zod4(searchFormSchema));

	return {
		form,
		cities,
		budgetOptions: BUDGET_OPTIONS,
		locationSettingOptions: LOCATION_SETTING_OPTIONS,
		dayOptions: DAY_OPTIONS
	};
};

export const actions: Actions = {
	search: async ({ request }) => {
		const form = await superValidate(request, zod4(searchFormSchema));

		if (!form.valid) {
			return fail(400, { form });
		}

		const { city, day, hour, locationSetting, budget } = form.data;

		try {
			const searchParams = {
				city,
				day: day || undefined,
				hour: hour || undefined,
				locationSetting: locationSetting || undefined,
				budget: budget || undefined
			};

			// Fetch ALL results — pagination is handled client-side
			const query = buildActivitySearchQuery(searchParams);
			const sparqlResult = await executeSparqlQuery(query);
			const activities: Activity[] = parseActivityResults(sparqlResult.results.bindings, searchParams);

			return {
				form,
				activities,
				totalCount: activities.length,
				searchCity: city.charAt(0).toUpperCase() + city.slice(1)
			};
		} catch (error) {
			console.error('Search query failed:', error);
			setError(form, 'city', 'Search failed. Please try again.');
			return fail(500, { form });
		}
	}
};
