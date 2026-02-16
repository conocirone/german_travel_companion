<script lang="ts">
    import { enhance } from '$app/forms';
    import type { PageProps } from './$types';
    import type { Activity } from '$lib/types';
    import type { SearchFormData } from '$lib/validation';
    import { PAGE_SIZE } from '$lib/types';
    import ActivityCard from '$lib/components/ActivityCard.svelte';
    import Pagination from '$lib/components/Pagination.svelte';

    let { data, form }: PageProps = $props();

    let isSubmitting = $state(false);
    let currentPage = $state(1);

    // Type guard for successful results
    function hasResults(f: typeof form): f is {
        success: true;
        activities: Activity[];
        totalCount: number;
        searchCity: string;
        searchParams: SearchFormData;
    } {
        return f !== null && f !== undefined && 'success' in f && f.success === true;
    }

    // Client-side pagination derived from form action result
    let allActivities = $derived(hasResults(form) ? form.activities : []);
    let totalCount = $derived(allActivities.length);
    let searchCity = $derived(hasResults(form) ? form.searchCity : '');
    let totalPages = $derived(Math.ceil(totalCount / PAGE_SIZE));
    let paginatedActivities = $derived(
        allActivities.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE)
    );

    // Preserve form values after submission
    const cityValue = $derived.by(() => {
        if (hasResults(form)) return form.searchParams.city ?? '';
        if (form?.values) return (form.values as Record<string, string>).city ?? '';
        return '';
    });
    const dayValue = $derived.by(() => {
        if (hasResults(form)) return form.searchParams.day ?? '';
        if (form?.values) return (form.values as Record<string, string>).day ?? '';
        return '';
    });
    const hourValue = $derived.by(() => {
        if (hasResults(form)) return form.searchParams.hour ?? '';
        if (form?.values) return (form.values as Record<string, string>).hour ?? '';
        return '';
    });
    const locationSettingValue = $derived.by(() => {
        if (hasResults(form)) return form.searchParams.locationSetting ?? '';
        if (form?.values) return (form.values as Record<string, string>).locationSetting ?? '';
        return '';
    });
    const budgetValue = $derived.by(() => {
        if (hasResults(form)) return form.searchParams.budget ?? '';
        if (form?.values) return (form.values as Record<string, string>).budget ?? '';
        return '';
    });

    function handlePageChange(page: number) {
        currentPage = page;
        document.querySelector('.results-section')?.scrollIntoView({ behavior: 'smooth' });
    }
</script>

<main>
    <h1>German Travel Companion</h1>
    <p>Search for tourism activities in German cities</p>

    <form
        method="POST"
        action="?/search"
        use:enhance={() => {
            isSubmitting = true;
            return async ({ update }) => {
                isSubmitting = false;
                currentPage = 1;
                await update();
            };
        }}
    >
        <div class="form-group">
            <label for="city">City</label>
            <select id="city" name="city" required value={cityValue}>
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
            <select id="day" name="day" value={dayValue}>
                <option value="">Any day...</option>
                {#each data.dayOptions as day}
                    <option value={day.value}>{day.label}</option>
                {/each}
            </select>
        </div>

        <div class="form-group">
            <label for="hour">Hour</label>
            <input type="time" id="hour" name="hour" value={hourValue} placeholder="HH:MM" />
        </div>

        <div class="form-group">
            <label for="locationSetting">Location Setting</label>
            <select id="locationSetting" name="locationSetting" value={locationSettingValue}>
                <option value="">Any setting...</option>
                {#each data.locationSettingOptions as setting}
                    <option value={setting.value}>{setting.label}</option>
                {/each}
            </select>
        </div>

        <div class="form-group">
            <label for="budget">Budget</label>
            <select id="budget" name="budget" value={budgetValue}>
                <option value="">Any budget...</option>
                {#each data.budgetOptions as budget}
                    <option value={budget.value}>{budget.label}</option>
                {/each}
            </select>
        </div>

        <button type="submit" disabled={isSubmitting}>
            {isSubmitting ? 'Searching...' : 'Search Activities'}
        </button>
    </form>

    {#if hasResults(form)}
        <section class="results-section">
            <div class="results-header">
                <h2>Activities in {searchCity}</h2>
                <p class="results-count">{totalCount} activities found</p>
            </div>

            {#if paginatedActivities.length > 0}
                <div class="results-grid">
                    {#each paginatedActivities as activity (activity.uri)}
                        <ActivityCard {activity} />
                    {/each}
                </div>

                {#if totalPages > 1}
                    <Pagination
                        {currentPage}
                        {totalPages}
                        {totalCount}
                        pageSize={PAGE_SIZE}
                        onPageChange={handlePageChange}
                    />
                {/if}
            {:else}
                <div class="no-results">
                    <p>No activities found matching your criteria.</p>
                    <p>Try adjusting your filters or selecting a different city.</p>
                </div>
            {/if}
        </section>
    {/if}
</main>

<style>
    main {
        max-width: 1200px;
        margin: 0 auto;
        padding: 2rem;
    }

    h1 {
        color: #333;
        margin-bottom: 0.5rem;
    }

    main > p {
        color: #666;
        margin-bottom: 2rem;
    }

    form {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        max-width: 800px;
        margin-bottom: 2rem;
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
        align-self: end;
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

    .results-section {
        margin-top: 2rem;
        padding-top: 2rem;
        border-top: 1px solid #e5e7eb;
    }

    .results-header {
        margin-bottom: 1.5rem;
    }

    .results-header h2 {
        color: #1f2937;
        font-size: 1.5rem;
        margin: 0 0 0.25rem 0;
    }

    .results-count {
        color: #6b7280;
        font-size: 0.95rem;
        margin: 0;
    }

    .results-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
        gap: 1.5rem;
    }

    .no-results {
        text-align: center;
        padding: 3rem 1rem;
        background-color: #f9fafb;
        border-radius: 8px;
        border: 1px dashed #d1d5db;
    }

    .no-results p {
        color: #6b7280;
        margin: 0.5rem 0;
    }

    .no-results p:first-child {
        font-size: 1.1rem;
        color: #374151;
        font-weight: 500;
    }

    @media (max-width: 768px) {
        form {
            grid-template-columns: 1fr;
        }

        .results-grid {
            grid-template-columns: 1fr;
        }
    }
</style>
