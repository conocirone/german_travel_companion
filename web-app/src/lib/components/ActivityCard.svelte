<script lang="ts">
    import type { Activity } from '$lib/types';

    interface Props {
        activity: Activity;
    }

    let { activity }: Props = $props();

    const typeColors: Record<string, string> = {
        Tour: '#6366f1',
        Museum: '#8b5cf6',
        Park: '#22c55e',
        Sight: '#f59e0b',
        NightlifeVenue: '#ec4899'
    };

    const budgetColors: Record<string, string> = {
        free: '#22c55e',
        low: '#3b82f6',
        medium: '#f59e0b',
        high: '#ef4444'
    };

    const typeColor = $derived(typeColors[activity.type] || '#6b7280');
    const budgetColor = $derived(activity.budget ? budgetColors[activity.budget] || '#6b7280' : '#6b7280');

    function formatType(type: string): string {
        if (type === 'NightlifeVenue') return 'Nightlife';
        return type;
    }

    function formatBudget(budget: string): string {
        return budget.charAt(0).toUpperCase() + budget.slice(1);
    }
</script>

<article class="card">
    <div class="card-image">
        {#if activity.imageUrl}
            <img src={activity.imageUrl} alt={activity.name} loading="lazy" />
        {:else}
            <div class="placeholder-image" style="background: linear-gradient(135deg, {typeColor}22, {typeColor}44);">
                <span class="placeholder-icon">
                    {#if activity.type === 'Tour'}🚶
                    {:else if activity.type === 'Museum'}🏛️
                    {:else if activity.type === 'Park'}🌳
                    {:else if activity.type === 'Sight'}📍
                    {:else if activity.type === 'NightlifeVenue'}🎉
                    {:else}📍
                    {/if}
                </span>
            </div>
        {/if}
        <span class="type-badge" style="background-color: {typeColor};">{formatType(activity.type)}</span>
    </div>

    <div class="card-content">
        <h3 class="card-title">{activity.name}</h3>

        <div class="card-meta">
            {#if activity.budget}
                <span class="budget-badge" style="background-color: {budgetColor}15; color: {budgetColor}; border: 1px solid {budgetColor}40;">
                    {formatBudget(activity.budget)}
                </span>
            {/if}

            {#if activity.locationSetting}
                <span class="setting-badge">
                    {#if activity.locationSetting === 'indoor'}🏢 Indoor{:else}🌤️ Outdoor{/if}
                </span>
            {/if}
        </div>

        {#if activity.duration}
            <p class="card-duration">⏱️ {activity.duration}</p>
        {/if}

        {#if activity.languages}
            <p class="card-languages" title={activity.languages}>🌐 {activity.languages.slice(0, 50)}{activity.languages.length > 50 ? '...' : ''}</p>
        {/if}

        {#if activity.meetingPoint}
            <p class="card-meeting-point" title={activity.meetingPoint}>📍 {activity.meetingPoint.slice(0, 60)}{activity.meetingPoint.length > 60 ? '...' : ''}</p>
        {/if}
    </div>

    {#if activity.url}
        <div class="card-actions">
            <a href={activity.url} target="_blank" rel="noopener noreferrer" class="card-link">
                View Details →
            </a>
        </div>
    {/if}
</article>

<style>
    .card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
        overflow: hidden;
        display: flex;
        flex-direction: column;
        transition: box-shadow 0.2s, transform 0.2s;
    }

    .card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        transform: translateY(-2px);
    }

    .card-image {
        position: relative;
        height: 180px;
        overflow: hidden;
    }

    .card-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .placeholder-image {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .placeholder-icon {
        font-size: 3rem;
    }

    .type-badge {
        position: absolute;
        top: 12px;
        right: 12px;
        padding: 4px 10px;
        border-radius: 20px;
        color: white;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.025em;
    }

    .card-content {
        padding: 1rem;
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #1f2937;
        margin: 0;
        line-height: 1.3;
    }

    .card-meta {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-top: 0.25rem;
    }

    .budget-badge,
    .setting-badge {
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 500;
    }

    .setting-badge {
        background-color: #f3f4f6;
        color: #4b5563;
    }

    .card-duration,
    .card-languages,
    .card-meeting-point {
        font-size: 0.85rem;
        color: #6b7280;
        margin: 0;
        line-height: 1.4;
    }

    .card-actions {
        padding: 0.75rem 1rem;
        border-top: 1px solid #f3f4f6;
        background-color: #fafafa;
    }

    .card-link {
        display: inline-block;
        color: #3b82f6;
        font-size: 0.9rem;
        font-weight: 500;
        text-decoration: none;
        transition: color 0.2s;
    }

    .card-link:hover {
        color: #1d4ed8;
        text-decoration: underline;
    }
</style>
