export interface City {
	uri: string;
	name: string;
	displayName: string;
}

export interface SelectOption {
	value: string;
	label: string;
}

export const BUDGET_OPTIONS: SelectOption[] = [
	{ value: 'budget_free', label: 'Free' },
	{ value: 'budget_low', label: 'Low' },
	{ value: 'budget_medium', label: 'Medium' },
	{ value: 'budget_high', label: 'High' }
];

export const LOCATION_SETTING_OPTIONS: SelectOption[] = [
	{ value: 'location_indoor', label: 'Indoor' },
	{ value: 'location_outdoor', label: 'Outdoor' }
];

export const DAY_OPTIONS: SelectOption[] = [
	{ value: 'monday', label: 'Monday' },
	{ value: 'tuesday', label: 'Tuesday' },
	{ value: 'wednesday', label: 'Wednesday' },
	{ value: 'thursday', label: 'Thursday' },
	{ value: 'friday', label: 'Friday' },
	{ value: 'saturday', label: 'Saturday' },
	{ value: 'sunday', label: 'Sunday' }
];

export type ActivityType = 'Tour' | 'Museum' | 'Park' | 'Sight' | 'NightlifeVenue';

export interface OperatingHour {
	day: string;
	opensAt: string;
	closesAt: string;
}

export interface Activity {
	uri: string;
	name: string;
	type: ActivityType;
	city: string;
	budget?: string;
	locationSetting?: string;
	imageUrl?: string;
	url?: string;
	duration?: string;
	languages?: string[];
	meetingPoint?: string;
	mapLink?: string;
	operatingHours?: OperatingHour[];
}

export interface PaginatedResults<T> {
	items: T[];
	totalCount: number;
	page: number;
	pageSize: number;
	totalPages: number;
}

export const PAGE_SIZE = 12;

/** Metadata for each SWRL-inferred class shortcut card. */
export interface ShortcutRule {
	key: string;
	label: string;
	emoji: string;
	description: string;
	color: string;
}

export const SHORTCUT_RULES: ShortcutRule[] = [
	{
		key: 'BudgetFriendlyActivity',
		label: 'Budget Friendly',
		emoji: '💰',
		description: 'Free or low-cost activities across all cities',
		color: 'from-emerald-500 to-emerald-700'
	},
	{
		key: 'BadWeatherOption',
		label: 'Bad Weather Options',
		emoji: '🌧️',
		description: 'Indoor activities for rainy days',
		color: 'from-cyan-500 to-cyan-700'
	},
	{
		key: 'EnglishFriendlyTour',
		label: 'English Friendly Tours',
		emoji: '🌐',
		description: 'Tours available in English for international visitors',
		color: 'from-indigo-500 to-indigo-700'
	},
	{
		key: 'OpenOnWeekend',
		label: 'Open on Weekends',
		emoji: '📅',
		description: 'Venues with Saturday or Sunday hours',
		color: 'from-purple-500 to-purple-700'
	}
];
