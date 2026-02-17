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

<nav class="flex flex-col items-center gap-4 py-6" aria-label="Pagination">
    <div class="text-sm text-gray-500">
        Showing <span class="font-semibold text-gray-700">{startItem}</span> – <span class="font-semibold text-gray-700">{endItem}</span> of <span class="font-semibold text-gray-700">{totalCount}</span> results
    </div>

    <div class="flex items-center gap-1.5">
        <button
            class="px-3.5 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            type="button"
            disabled={currentPage <= 1}
            onclick={() => goToPage(currentPage - 1)}
            aria-label="Previous page"
        >
            ← Prev
        </button>

        <div class="flex items-center gap-1">
            {#each visiblePages as page, i}
                {#if page === 'ellipsis'}
                    <span class="w-8 text-center text-gray-400 text-sm" aria-hidden="true">…</span>
                {:else}
                    <button
                        class="min-w-9 h-9 px-2 text-sm font-medium rounded-lg transition-all
                            {page === currentPage
                                ? 'bg-primary-600 text-white border border-primary-600 shadow-sm'
                                : 'text-gray-600 bg-white border border-gray-200 hover:bg-gray-50 hover:border-gray-300'}"
                        type="button"
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
            class="px-3.5 py-2 text-sm font-medium text-gray-600 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 hover:border-gray-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
            type="button"
            disabled={currentPage >= totalPages}
            onclick={() => goToPage(currentPage + 1)}
            aria-label="Next page"
        >
            Next →
        </button>
    </div>
</nav>
