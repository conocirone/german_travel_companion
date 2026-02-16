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

export interface QueryFormData {
	city: string;
	day: string;
	hour: string;
	locationSetting: string;
	budget: string;
}

export type ActivityType = 'Tour' | 'Museum' | 'Park' | 'Sight' | 'NightlifeVenue';

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
	languages?: string;
	meetingPoint?: string;
}

export interface PaginatedResults<T> {
	items: T[];
	totalCount: number;
	page: number;
	pageSize: number;
	totalPages: number;
}

export const PAGE_SIZE = 12;
