<script lang="ts">
    interface Props {
        currentPage: number;
        totalPages: number;
        totalCount: number;
        pageSize: number;
        onPageChange: (page: number) => void;
    }

    let { currentPage, totalPages, totalCount, pageSize, onPageChange }: Props = $props();

    const startItem = $derived((currentPage - 1) * pageSize + 1);
    const endItem = $derived(Math.min(currentPage * pageSize, totalCount));

    const visiblePages = $derived.by(() => {
        const pages: (number | 'ellipsis')[] = [];
        const maxVisible = 5;

        if (totalPages <= maxVisible + 2) {
            // Show all pages
            for (let i = 1; i <= totalPages; i++) {
                pages.push(i);
            }
        } else {
            // Always show first page
            pages.push(1);

            if (currentPage > 3) {
                pages.push('ellipsis');
            }

            // Show pages around current
            const start = Math.max(2, currentPage - 1);
            const end = Math.min(totalPages - 1, currentPage + 1);

            for (let i = start; i <= end; i++) {
                pages.push(i);
            }

            if (currentPage < totalPages - 2) {
                pages.push('ellipsis');
            }

            // Always show last page
            pages.push(totalPages);
        }

        return pages;
    });

    function goToPage(page: number) {
        if (page >= 1 && page <= totalPages && page !== currentPage) {
            onPageChange(page);
        }
    }
</script>

<nav class="pagination" aria-label="Pagination">
    <div class="pagination-info">
        Showing <strong>{startItem}</strong> - <strong>{endItem}</strong> of <strong>{totalCount}</strong> results
    </div>

    <div class="pagination-controls">
        <button
            class="pagination-btn"
            type="button"
            disabled={currentPage <= 1}
            onclick={() => goToPage(currentPage - 1)}
            aria-label="Previous page"
        >
            ← Previous
        </button>

        <div class="pagination-pages">
            {#each visiblePages as page, i}
                {#if page === 'ellipsis'}
                    <span class="pagination-ellipsis" aria-hidden="true">…</span>
                {:else}
                    <button
                        class="pagination-page"
                        type="button"
                        class:active={page === currentPage}
                        onclick={() => goToPage(page)}
                        aria-label="Go to page {page}"
                        aria-current={page === currentPage ? 'page' : undefined}
                    >
                        {page}
                    </button>
                {/if}
            {/each}
        </div>

        <button
            class="pagination-btn"
            type="button"
            disabled={currentPage >= totalPages}
            onclick={() => goToPage(currentPage + 1)}
            aria-label="Next page"
        >
            Next →
        </button>
    </div>
</nav>

<style>
    .pagination {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        padding: 1.5rem 0;
    }

    .pagination-info {
        color: #6b7280;
        font-size: 0.9rem;
    }

    .pagination-info strong {
        color: #374151;
    }

    .pagination-controls {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .pagination-btn {
        padding: 0.5rem 1rem;
        font-size: 0.9rem;
        font-weight: 500;
        color: #374151;
        background-color: white;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .pagination-btn:hover:not(:disabled) {
        background-color: #f9fafb;
        border-color: #9ca3af;
    }

    .pagination-btn:disabled {
        color: #9ca3af;
        cursor: not-allowed;
        opacity: 0.6;
    }

    .pagination-pages {
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }

    .pagination-page {
        min-width: 2.5rem;
        height: 2.5rem;
        padding: 0 0.5rem;
        font-size: 0.9rem;
        font-weight: 500;
        color: #374151;
        background-color: white;
        border: 1px solid #d1d5db;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.2s;
    }

    .pagination-page:hover:not(.active) {
        background-color: #f9fafb;
        border-color: #9ca3af;
    }

    .pagination-page.active {
        background-color: #3b82f6;
        border-color: #3b82f6;
        color: white;
    }

    .pagination-ellipsis {
        min-width: 2rem;
        text-align: center;
        color: #6b7280;
    }

    @media (max-width: 640px) {
        .pagination-controls {
            flex-wrap: wrap;
            justify-content: center;
        }

        .pagination-btn {
            padding: 0.5rem 0.75rem;
            font-size: 0.85rem;
        }

        .pagination-page {
            min-width: 2rem;
            height: 2rem;
            font-size: 0.85rem;
        }
    }
</style>
