<script lang="ts">
    import { superForm } from 'sveltekit-superforms';
    import type { PageProps } from './$types';
    import type { Activity } from '$lib/types';
    import { PAGE_SIZE } from '$lib/types';
    import ActivityCard from '$lib/components/ActivityCard.svelte';
    import Pagination from '$lib/components/Pagination.svelte';

    let { data }: PageProps = $props();

    // Search results state
    let activities = $state<Activity[]>([]);
    let searchCity = $state('');
    let searchComplete = $state(false);
    let currentPage = $state(1);

    const { form: formData, errors, enhance, submitting } = superForm(data.form, {
        resetForm: false,
        onResult({ result }) {
            if (result.type === 'success' && result.data) {
                const { activities: acts, searchCity: city } = result.data as {
                    activities: Activity[];
                    searchCity: string;
                };
                activities = acts;
                searchCity = city;
                searchComplete = true;
                currentPage = 1;
            }
        }
    });

    // Client-side pagination
    let totalCount = $derived(activities.length);
    let totalPages = $derived(Math.ceil(totalCount / PAGE_SIZE));
    let paginatedActivities = $derived(
        activities.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE)
    );

    function handlePageChange(page: number) {
        currentPage = page;
        document.querySelector('.results-section')?.scrollIntoView({ behavior: 'smooth' });
    }

    // City images from Unsplash for hero background variety
    const cityImages: Record<string, string> = {
        berlin: 'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=1920&q=80',
        munich: 'https://images.unsplash.com/photo-1595867818082-083862f3d630?w=1920&q=80',
        hamburg: 'https://images.unsplash.com/photo-1569150216991-aba1feb19ac5?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        cologne: 'https://images.unsplash.com/photo-1561624485-0e43bcc1836d?q=80&w=1740&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        frankfurt: 'https://images.unsplash.com/photo-1648305857224-a2ef55b086f5?q=80&w=1666&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        dresden: 'https://images.unsplash.com/photo-1619120810930-6ca5048deee1?q=80&w=2662&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        dusseldorf: 'https://images.unsplash.com/photo-1653559082653-3cba57090b69?q=80&w=2620&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D',
        default: 'https://images.unsplash.com/photo-1560969184-10fe8719e047?w=1920&q=80'
    };

    let heroImage = $derived(
        searchCity
            ? cityImages[searchCity.toLowerCase()] || cityImages.default
            : cityImages.default
    );
</script>

<!-- Hero Section -->
<section class="relative overflow-hidden bg-linear-to-br from-primary-900 via-primary-800 to-primary-700">
    <!-- Background image overlay -->
    <div
        class="absolute inset-0 bg-cover bg-center transition-all duration-700"
        style="background-image: url('{heroImage}'); opacity: 0.15;"
    ></div>
    <!-- Gradient overlay -->
    <div class="absolute inset-0 bg-linear-to-b from-primary-900/70 via-primary-800/60 to-primary-700/80"></div>

    <!-- Decorative elements -->
    <div class="absolute top-0 left-0 w-72 h-72 bg-accent-400/5 rounded-full -translate-x-1/2 -translate-y-1/2"></div>
    <div class="absolute bottom-0 right-0 w-96 h-96 bg-accent-400/5 rounded-full translate-x-1/3 translate-y-1/3"></div>

    <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        <div class="text-center mb-8 md:mb-10">
            <h1 class="text-3xl md:text-5xl font-extrabold text-white mb-3 tracking-tight">
                Explore <span class="text-accent-300">Germany</span>
            </h1>
            <p class="text-primary-200 text-lg md:text-xl max-w-2xl mx-auto font-light">
                Discover curated tours, museums, parks, and nightlife across Germany's most vibrant cities
            </p>
        </div>

        <!-- Search Form Card -->
        <div class="max-w-4xl mx-auto">
            <form
                method="POST"
                action="?/search"
                use:enhance
                class="bg-white/10 backdrop-blur-xl rounded-2xl p-6 md:p-8 border border-white/20 shadow-2xl"
            >
                <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 md:gap-5">
                    <!-- City -->
                    <div class="sm:col-span-2 lg:col-span-1">
                        <label for="city" class="block text-sm font-semibold text-white/90 mb-1.5">
                            🏙️ City
                        </label>
                        <select
                            id="city"
                            name="city"
                            required
                            bind:value={$formData.city}
                            class="w-full rounded-xl bg-white/90 backdrop-blur text-gray-800 border-0 px-4 py-3 text-base shadow-sm focus:ring-2 focus:ring-accent-400 focus:bg-white transition"
                        >
                            <option value="">Select a city...</option>
                            {#each data.cities as city}
                                <option value={city.name}>{city.displayName}</option>
                            {/each}
                        </select>
                        {#if $errors.city}
                            <span class="text-red-300 text-sm mt-1 block">{$errors.city}</span>
                        {/if}
                    </div>

                    <!-- Day -->
                    <div>
                        <label for="day" class="block text-sm font-semibold text-white/90 mb-1.5">
                            📅 Day
                        </label>
                        <select
                            id="day"
                            name="day"
                            bind:value={$formData.day}
                            class="w-full rounded-xl bg-white/90 backdrop-blur text-gray-800 border-0 px-4 py-3 text-base shadow-sm focus:ring-2 focus:ring-accent-400 focus:bg-white transition"
                        >
                            <option value="">Any day...</option>
                            {#each data.dayOptions as day}
                                <option value={day.value}>{day.label}</option>
                            {/each}
                        </select>
                    </div>

                    <!-- Hour -->
                    <div>
                        <label for="hour" class="block text-sm font-semibold text-white/90 mb-1.5">
                            🕐 Hour
                        </label>
                        <input
                            type="time"
                            id="hour"
                            name="hour"
                            bind:value={$formData.hour}
                            placeholder="HH:MM"
                            class="w-full rounded-xl bg-white/90 backdrop-blur text-gray-800 border-0 px-4 py-3 text-base shadow-sm focus:ring-2 focus:ring-accent-400 focus:bg-white transition"
                        />
                    </div>

                    <!-- Location Setting -->
                    <div>
                        <label for="locationSetting" class="block text-sm font-semibold text-white/90 mb-1.5">
                            📍 Setting
                        </label>
                        <select
                            id="locationSetting"
                            name="locationSetting"
                            bind:value={$formData.locationSetting}
                            class="w-full rounded-xl bg-white/90 backdrop-blur text-gray-800 border-0 px-4 py-3 text-base shadow-sm focus:ring-2 focus:ring-accent-400 focus:bg-white transition"
                        >
                            <option value="">Any setting...</option>
                            {#each data.locationSettingOptions as setting}
                                <option value={setting.value}>{setting.label}</option>
                            {/each}
                        </select>
                    </div>

                    <!-- Budget -->
                    <div>
                        <label for="budget" class="block text-sm font-semibold text-white/90 mb-1.5">
                            💰 Budget
                        </label>
                        <select
                            id="budget"
                            name="budget"
                            bind:value={$formData.budget}
                            class="w-full rounded-xl bg-white/90 backdrop-blur text-gray-800 border-0 px-4 py-3 text-base shadow-sm focus:ring-2 focus:ring-accent-400 focus:bg-white transition"
                        >
                            <option value="">Any budget...</option>
                            {#each data.budgetOptions as budget}
                                <option value={budget.value}>{budget.label}</option>
                            {/each}
                        </select>
                    </div>

                    <!-- Submit Button -->
                    <div class="flex items-end">
                        <button
                            type="submit"
                            disabled={$submitting}
                            class="w-full rounded-xl px-6 py-3 text-base font-bold text-primary-900 bg-accent-400 hover:bg-accent-300 active:bg-accent-500 disabled:bg-gray-400 disabled:text-gray-600 disabled:cursor-not-allowed shadow-lg hover:shadow-xl transition-all duration-200 cursor-pointer"
                        >
                            {#if $submitting}
                                <span class="inline-flex items-center gap-2">
                                    <svg class="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Searching...
                                </span>
                            {:else}
                                Search Activities
                            {/if}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    </div>

    <!-- Wave divider -->
    <div class="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 60" fill="none" xmlns="http://www.w3.org/2000/svg" class="w-full" preserveAspectRatio="none">
            <path d="M0 60L48 55C96 50 192 40 288 35C384 30 480 30 576 33.3C672 36.7 768 43.3 864 45C960 46.7 1056 43.3 1152 38.3C1248 33.3 1344 26.7 1392 23.3L1440 20V60H1392C1344 60 1248 60 1152 60C1056 60 960 60 864 60C768 60 672 60 576 60C480 60 384 60 288 60C192 60 96 60 48 60H0Z" fill="#f8fafc"/>
        </svg>
    </div>
</section>

<!-- Results Section -->
{#if searchComplete}
    <section class="results-section max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
        <!-- Results header -->
        <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-6">
            <div>
                <h2 class="text-2xl md:text-3xl font-bold text-gray-900">
                    Activities in <span class="text-primary-600">{searchCity}</span>
                </h2>
                <p class="text-gray-500 mt-1">
                    {totalCount} {totalCount === 1 ? 'activity' : 'activities'} found
                </p>
            </div>
            {#if totalCount > 0}
                <div class="flex items-center gap-2 text-sm text-gray-400">
                    <span class="inline-block w-2 h-2 rounded-full bg-green-400"></span>
                    Page {currentPage} of {totalPages}
                </div>
            {/if}
        </div>

        {#if paginatedActivities.length > 0}
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5 md:gap-6">
                {#each paginatedActivities as activity (activity.uri)}
                    <ActivityCard {activity} />
                {/each}
            </div>

            {#if totalPages > 1}
                <div class="mt-8">
                    <Pagination
                        {currentPage}
                        {totalPages}
                        {totalCount}
                        pageSize={PAGE_SIZE}
                        onPageChange={handlePageChange}
                    />
                </div>
            {/if}
        {:else}
            <div class="text-center py-16 px-6 bg-gray-50 rounded-2xl border border-dashed border-gray-200">
                <div class="text-5xl mb-4">🔍</div>
                <p class="text-lg font-medium text-gray-700 mb-2">No activities found</p>
                <p class="text-gray-500 max-w-md mx-auto">
                    Try adjusting your filters or selecting a different city to discover more activities.
                </p>
            </div>
        {/if}
    </section>
{:else}
    <!-- Default state: City showcase cards -->
    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 md:py-16">
        <h2 class="text-xl font-bold text-gray-800 mb-6 text-center">Popular Destinations</h2>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 md:gap-6">
            {#each [
                { name: 'Berlin', emoji: '🏛️', desc: 'History & Culture', color: 'from-blue-500 to-blue-700' },
                { name: 'Munich', emoji: '🏰', desc: 'Bavarian Charm', color: 'from-emerald-500 to-emerald-700' },
                { name: 'Hamburg', emoji: '⚓', desc: 'Maritime Spirit', color: 'from-cyan-500 to-cyan-700' },
                { name: 'Cologne', emoji: '⛪', desc: 'Gothic Grandeur', color: 'from-purple-500 to-purple-700' }
            ] as city}
                <div class="bg-linear-to-br {city.color} rounded-2xl p-6 text-white shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all duration-300 cursor-default">
                    <div class="text-3xl mb-2">{city.emoji}</div>
                    <h3 class="text-lg font-bold">{city.name}</h3>
                    <p class="text-white/70 text-sm mt-1">{city.desc}</p>
                </div>
            {/each}
        </div>
        <p class="text-center text-gray-400 text-sm mt-8">
            Select a city above to start exploring activities
        </p>
    </section>
{/if}
