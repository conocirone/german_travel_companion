<script lang="ts">
    import type { Activity } from '$lib/types';

    interface Props {
        activity: Activity;
    }

    let { activity }: Props = $props();

    const typeConfig: Record<string, { color: string; bg: string; icon: string }> = {
        Tour: { color: '#6366f1', bg: '#eef2ff', icon: '🚶' },
        Museum: { color: '#7c3aed', bg: '#f5f3ff', icon: '🏛️' },
        Park: { color: '#16a34a', bg: '#f0fdf4', icon: '🌳' },
        Sight: { color: '#d97706', bg: '#fffbeb', icon: '📍' },
        NightlifeVenue: { color: '#db2777', bg: '#fdf2f8', icon: '🎉' }
    };

    const budgetConfig: Record<string, { color: string; bg: string; label: string }> = {
        free: { color: '#16a34a', bg: '#f0fdf4', label: 'Free' },
        low: { color: '#2563eb', bg: '#eff6ff', label: 'Low' },
        medium: { color: '#d97706', bg: '#fffbeb', label: 'Medium' },
        high: { color: '#dc2626', bg: '#fef2f2', label: 'High' }
    };

    const type = $derived(typeConfig[activity.type] || { color: '#6b7280', bg: '#f3f4f6', icon: '📍' });
    const budget = $derived(activity.budget ? budgetConfig[activity.budget] : null);

    function formatType(t: string): string {
        if (t === 'NightlifeVenue') return 'Nightlife';
        return t;
    }
</script>

<article class="group bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-lg hover:-translate-y-1 transition-all duration-300 flex flex-col">
    <!-- Image / Placeholder -->
    <div class="relative h-44 overflow-hidden">
        {#if activity.imageUrl}
            <img
                src={activity.imageUrl}
                alt={activity.name}
                loading="lazy"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
            />
            <div class="absolute inset-0 bg-linear-to-t from-black/30 to-transparent"></div>
        {:else}
            <div
                class="w-full h-full flex items-center justify-center"
                style="background: linear-gradient(135deg, {type.bg}, {type.color}15);"
            >
                <span class="text-5xl opacity-80 group-hover:scale-110 transition-transform duration-300">{type.icon}</span>
            </div>
        {/if}
        <!-- Type badge -->
        <span
            class="absolute top-3 right-3 px-3 py-1 rounded-full text-white text-xs font-bold uppercase tracking-wide shadow-md"
            style="background-color: {type.color};"
        >
            {formatType(activity.type)}
        </span>
    </div>

    <!-- Content -->
    <div class="flex-1 p-4 flex flex-col gap-2.5">
        <h3 class="text-base font-bold text-gray-900 leading-snug line-clamp-2">
            {activity.name}
        </h3>

        <!-- Tags row -->
        <div class="flex flex-wrap gap-1.5">
            {#if budget}
                <span
                    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold"
                    style="background-color: {budget.bg}; color: {budget.color};"
                >
                    💰 {budget.label}
                </span>
            {/if}
            {#if activity.locationSetting}
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold bg-gray-100 text-gray-600">
                    {activity.locationSetting === 'indoor' ? '🏢 Indoor' : '🌤️ Outdoor'}
                </span>
            {/if}
        </div>

        <!-- Details -->
        <div class="flex flex-col gap-1 mt-auto text-sm text-gray-500">
            {#if activity.duration}
                <p class="flex items-center gap-1.5 m-0">
                    <span class="text-xs">⏱️</span> {activity.duration}
                </p>
            {/if}
            {#if activity.languages}
                <p class="flex items-center gap-1.5 m-0 truncate" title={activity.languages}>
                    <span class="text-xs">🌐</span> {activity.languages.slice(0, 45)}{activity.languages.length > 45 ? '...' : ''}
                </p>
            {/if}
            {#if activity.meetingPoint}
                <p class="flex items-center gap-1.5 m-0 truncate" title={activity.meetingPoint}>
                    <span class="text-xs">📍</span> {activity.meetingPoint.slice(0, 50)}{activity.meetingPoint.length > 50 ? '...' : ''}
                </p>
            {/if}
        </div>
    </div>

    <!-- Action -->
    {#if activity.url}
        <div class="px-4 py-3 border-t border-gray-50 bg-gray-50/50">
            <a
                href={activity.url}
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center gap-1.5 text-sm font-semibold text-primary-600 hover:text-primary-800 no-underline transition-colors"
            >
                View Details
                <svg class="w-4 h-4 group-hover:translate-x-0.5 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
            </a>
        </div>
    {/if}
</article>
