<script lang="ts">
	import type { PageProps } from './$types';

	let { data }: PageProps = $props();

	let selectedCity = $state('');
	let selectedDay = $state('');
	let selectedHour = $state('');
	let selectedLocationSetting = $state('');
	let selectedBudget = $state('');

	function handleSubmit(event: SubmitEvent) {
		event.preventDefault();
		// Query execution will be implemented in the next phase
		console.log('Form submitted:', {
			city: selectedCity,
			day: selectedDay,
			hour: selectedHour,
			locationSetting: selectedLocationSetting,
			budget: selectedBudget
		});
	}
</script>

<main>
	<h1>German Travel Companion</h1>
	<p>Search for tourism activities in German cities</p>

	<form onsubmit={handleSubmit}>
		<div class="form-group">
			<label for="city">City</label>
			<select id="city" bind:value={selectedCity} required>
				<option value="">Select a city...</option>
				{#each data.cities as city}
					<option value={city.name}>{city.displayName}</option>
				{/each}
			</select>
		</div>

		<div class="form-group">
			<label for="day">Day</label>
			<select id="day" bind:value={selectedDay}>
				<option value="">Any day...</option>
				{#each data.dayOptions as day}
					<option value={day.value}>{day.label}</option>
				{/each}
			</select>
		</div>

		<div class="form-group">
			<label for="hour">Hour</label>
			<input
				type="time"
				id="hour"
				bind:value={selectedHour}
				placeholder="HH:MM"
			/>
		</div>

		<div class="form-group">
			<label for="locationSetting">Location Setting</label>
			<select id="locationSetting" bind:value={selectedLocationSetting}>
				<option value="">Any setting...</option>
				{#each data.locationSettingOptions as setting}
					<option value={setting.value}>{setting.label}</option>
				{/each}
			</select>
		</div>

		<div class="form-group">
			<label for="budget">Budget</label>
			<select id="budget" bind:value={selectedBudget}>
				<option value="">Any budget...</option>
				{#each data.budgetOptions as budget}
					<option value={budget.value}>{budget.label}</option>
				{/each}
			</select>
		</div>

		<button type="submit">Search Activities</button>
	</form>
</main>

<style>
	main {
		max-width: 600px;
		margin: 0 auto;
		padding: 2rem;
	}

	h1 {
		color: #333;
		margin-bottom: 0.5rem;
	}

	p {
		color: #666;
		margin-bottom: 2rem;
	}

	form {
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.form-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	label {
		font-weight: 600;
		color: #444;
	}

	select,
	input[type='time'] {
		padding: 0.75rem;
		font-size: 1rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		background-color: white;
	}

	select:focus,
	input[type='time']:focus {
		outline: none;
		border-color: #007bff;
		box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
	}

	button[type='submit'] {
		padding: 0.875rem 1.5rem;
		font-size: 1rem;
		font-weight: 600;
		color: white;
		background-color: #007bff;
		border: none;
		border-radius: 4px;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	button[type='submit']:hover {
		background-color: #0056b3;
	}

	button[type='submit']:active {
		background-color: #004494;
	}
</style>
