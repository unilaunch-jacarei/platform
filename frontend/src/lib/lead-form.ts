export type LeadFormValues = {
	full_name?: string;
	email?: string;
	company_name?: string;
	job_title?: string;
	company_size?: string;
	website?: string;
	message?: string;
	privacy_consent?: boolean;
};

export type StudentLeadFormValues = {
	full_name?: string;
	email?: string;
	institution_id?: string;
	institution_name?: string;
	institution_name_display?: string;
	course_id?: string;
	course_name?: string;
	course_name_display?: string;
	semester_number?: string;
	linkedin_url?: string;
	github_url?: string;
	interest_area_ids?: string[];
	message?: string;
	privacy_consent?: boolean;
};

export type StudentLeadPayload = {
	full_name?: string;
	email?: string;
	institution_id?: string;
	institution_name?: string;
	course_id?: string;
	course_name?: string;
	semester_number?: number;
	linkedin_url?: string;
	github_url?: string;
	interest_area_ids: string[];
	message?: string;
	privacy_consent?: boolean;
};

export type CatalogOption = { id: string; name: string };
export type InterestAreaOption = CatalogOption & { code: string };
