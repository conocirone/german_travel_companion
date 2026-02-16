import { z } from 'zod';

export const searchFormSchema = z.object({
    city: z.string().min(1, 'City is required'),
    day: z.string().optional().default(''),
    hour: z.string().optional().default(''),
    locationSetting: z.string().optional().default(''),
    budget: z.string().optional().default('')
});

export type SearchFormData = z.infer<typeof searchFormSchema>;

export interface SearchFormErrors {
    city?: string[];
    day?: string[];
    hour?: string[];
    locationSetting?: string[];
    budget?: string[];
}