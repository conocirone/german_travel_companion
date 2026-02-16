import type { Actions, PageServerLoad } from './$types';
import { SPARQL_PREFIXES, ONTOLOGY_PREFIX } from '$lib/sparql';
import { executeSparqlQuery, buildActivitySearchQuery, parseActivityResults } from '$lib/sparql';
import { BUDGET_OPTIONS, LOCATION_SETTING_OPTIONS, DAY_OPTIONS, type City, type Activity } from '$lib/types';
import { searchFormSchema } from '$lib/validation';
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
			const errors: Record<string, string[]> = {};
			for (const issue of result.error.issues) {
				const field = issue.path[0] as string;
				if (!errors[field]) errors[field] = [];
				errors[field].push(issue.message);
			}
			return fail(400, { errors, values: rawData });
		}

		const { city, day, hour, locationSetting, budget } = result.data;

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
			const activities = parseActivityResults(sparqlResult.results.bindings, searchParams);

			return {
				success: true as const,
				activities,
				totalCount: activities.length,
				searchCity: city.charAt(0).toUpperCase() + city.slice(1),
				searchParams: result.data
			};
		} catch (error) {
			console.error('Search query failed:', error);
			return fail(500, {
				errors: { city: ['Search failed. Please try again.'] },
				values: rawData
			});
		}
	}
};
