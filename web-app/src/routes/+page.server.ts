import type { Actions, PageServerLoad } from './$types';
import { SPARQL_PREFIXES, ONTOLOGY_PREFIX } from '$lib/sparql';
import { executeSparqlQuery, buildActivitySearchQuery, buildShortcutQuery, parseActivityResults, extractCityFromUri } from '$lib/sparql';
import { BUDGET_OPTIONS, LOCATION_SETTING_OPTIONS, DAY_OPTIONS, SHORTCUT_RULES, type City, type Activity } from '$lib/types';
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
	const cities = (await fetchCities()).filter(city => city.name !== 'leipzig'); // Filter out 'unknown' city if it exists
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
			console.log('Generated SPARQL query:', query);
			const sparqlResult = await executeSparqlQuery(query);
			const cityName = city.charAt(0).toUpperCase() + city.slice(1);
			const activities: Activity[] = parseActivityResults(
				sparqlResult.results.bindings,
				() => cityName
			);

			// Shuffle activities so results aren't grouped by type
			for (let i = activities.length - 1; i > 0; i--) {
				const j = Math.floor(Math.random() * (i + 1));
				[activities[i], activities[j]] = [activities[j], activities[i]];
			}

			return {
				form,
				activities,
				totalCount: activities.length,
				searchCity: city.charAt(0).toUpperCase() + city.slice(1),
				searchTitle: `Activities in ${city.charAt(0).toUpperCase() + city.slice(1)}`
			};
		} catch (error) {
			console.error('Search query failed:', error);
			setError(form, 'city', 'Search failed. Please try again.');
			return fail(500, { form });
		}
	},

	shortcut: async ({ request }) => {
		const formData = await request.formData();
		const rule = formData.get('rule')?.toString() ?? '';

		const validKeys = SHORTCUT_RULES.map((r) => r.key);
		if (!validKeys.includes(rule)) {
			return fail(400, { error: `Invalid shortcut rule: ${rule}` });
		}

		try {
			const ruleInfo = SHORTCUT_RULES.find((r) => r.key === rule)!;
			const query = buildShortcutQuery(rule);
			console.log('Generated shortcut SPARQL query:', query);
			const sparqlResult = await executeSparqlQuery(query);
			const activities: Activity[] = parseActivityResults(
				sparqlResult.results.bindings,
				(binding) => binding.cityUri ? extractCityFromUri(binding.cityUri.value) : 'Unknown'
			);

			// Shuffle activities so results aren't grouped by type
			for (let i = activities.length - 1; i > 0; i--) {
				const j = Math.floor(Math.random() * (i + 1));
				[activities[i], activities[j]] = [activities[j], activities[i]];
			}

			return {
				activities,
				totalCount: activities.length,
				searchTitle: ruleInfo.label
			};
		} catch (error) {
			console.error('Shortcut query failed:', error);
			return fail(500, { error: 'Shortcut query failed. Please try again.' });
		}
	}
};
