<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg';

	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin="anonymous" />
	<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
	<title>German Travel Companion</title>
</svelte:head>

<div class="min-h-screen flex flex-col">
	<!-- Header -->
	<header class="bg-linear-to-r from-primary-900 via-primary-800 to-primary-700 text-white shadow-lg">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
			<div class="flex items-center justify-between h-16">
				<a href="/" class="flex items-center gap-3 no-underline text-white">
					<span class="text-2xl">🧭</span>
					<div>
						<span class="text-lg font-bold tracking-tight">German Travel Companion</span>
						<span class="hidden sm:inline-block ml-2 text-xs font-medium bg-accent-400/20 text-accent-200 px-2 py-0.5 rounded-full">Beta</span>
					</div>
				</a>
				<nav class="flex items-center gap-2">
					<span class="text-xs text-primary-300 hidden md:block">Discover Germany's best activities</span>
					<!-- German flag mini -->
					<div class="flex flex-col gap-0 ml-3">
						<div class="w-6 h-1.5 bg-black rounded-t-sm"></div>
						<div class="w-6 h-1.5 bg-red-600"></div>
						<div class="w-6 h-1.5 bg-yellow-400 rounded-b-sm"></div>
					</div>
				</nav>
			</div>
		</div>
	</header>

	<!-- Main content -->
	<main class="flex-1">
		{@render children()}
	</main>

	<!-- Footer -->
	<footer class="bg-gray-900 text-gray-400 mt-auto">
		<div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
			<div class="flex flex-col sm:flex-row items-center justify-between gap-4">
				<div class="flex items-center gap-2">
					<span class="text-lg">🧭</span>
					<span class="text-sm font-medium text-gray-300">German Travel Companion</span>
				</div>
				<p class="text-xs text-gray-500">
					Powered by Knowledge Representation &amp; SPARQL ontologies — Bielefeld University
				</p>
			</div>
		</div>
	</footer>
</div>
