<script lang="ts">
    import { enhance } from '$app/forms';
    import type { PageProps } from './$types';

    let { data, form }: PageProps = $props();

    let isSubmitting = $state(false);
</script>

<main>
    <h1>German Travel Companion</h1>
    <p>Search for tourism activities in German cities</p>

    {#if form?.success}
        <div class="success-message">
            <p>Search submitted successfully!</p>
            <pre>{JSON.stringify(form.searchParams, null, 2)}</pre>
        </div>
    {/if}

    <form
        method="POST"
        action="?/search"
        use:enhance={() => {
            isSubmitting = true;
            return async ({ update }) => {
                isSubmitting = false;
                await update();
            };
        }}
    >
        <div class="form-group">
            <label for="city">City</label>
            <select id="city" name="city" required value={form?.values?.city ?? ''}>
                <option value="">Select a city...</option>
                {#each data.cities as city}
                    <option value={city.name}>{city.displayName}</option>
                {/each}
            </select>
            {#if form?.errors?.city}
                <span class="error">{form.errors.city.join(', ')}</span>
            {/if}
        </div>

        <div class="form-group">
            <label for="day">Day</label>
            <select id="day" name="day" value={form?.values?.day ?? ''}>
                <option value="">Any day...</option>
                {#each data.dayOptions as day}
                    <option value={day.value}>{day.label}</option>
                {/each}
            </select>
            {#if form?.errors?.day}
                <span class="error">{form.errors.day.join(', ')}</span>
            {/if}
        </div>

        <div class="form-group">
            <label for="hour">Hour</label>
            <input type="time" id="hour" name="hour" value={form?.values?.hour ?? ''} placeholder="HH:MM" />
            {#if form?.errors?.hour}
                <span class="error">{form.errors.hour.join(', ')}</span>
            {/if}
        </div>

        <div class="form-group">
            <label for="locationSetting">Location Setting</label>
            <select id="locationSetting" name="locationSetting" value={form?.values?.locationSetting ?? ''}>
                <option value="">Any setting...</option>
                {#each data.locationSettingOptions as setting}
                    <option value={setting.value}>{setting.label}</option>
                {/each}
            </select>
            {#if form?.errors?.locationSetting}
                <span class="error">{form.errors.locationSetting.join(', ')}</span>
            {/if}
        </div>

        <div class="form-group">
            <label for="budget">Budget</label>
            <select id="budget" name="budget" value={form?.values?.budget ?? ''}>
                <option value="">Any budget...</option>
                {#each data.budgetOptions as budget}
                    <option value={budget.value}>{budget.label}</option>
                {/each}
            </select>
            {#if form?.errors?.budget}
                <span class="error">{form.errors.budget.join(', ')}</span>
            {/if}
        </div>

        <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Searching...' : 'Search Activities'}
        </button>
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

    .error {
        color: #dc3545;
        font-size: 0.875rem;
    }

    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 4px;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }

    .success-message p {
        color: #155724;
        margin-bottom: 0.5rem;
    }

    .success-message pre {
        background-color: #f8f9fa;
        padding: 0.5rem;
        border-radius: 4px;
        font-size: 0.875rem;
        overflow-x: auto;
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

    button[type='submit']:hover:not(:disabled) {
        background-color: #0056b3;
    }

    button[type='submit']:active:not(:disabled) {
        background-color: #004494;
    }

    button[type='submit']:disabled {
        background-color: #6c757d;
        cursor: not-allowed;
    }
</style>
