export type UserRole = 'worker' | 'verifier' | 'advocate';

export interface User {
  id: string;
  email: string;
  role: UserRole;
  created_at: string;
  updated_at: string;
}

export interface Worker extends User {
  full_name: string;
  city_zone: string;
  primary_platform: string;
  category: string;
  verified_entries_count: number;
  profile_url?: string;
  bio?: string;
}

export interface EarningsEntry {
  id: string;
  worker_id: string;
  platform: string;
  entry_date: string;
  hours_worked: number;
  gross_earned: number;
  platform_deductions: number;
  net_received: number;
  deduction_percentage?: number;
  hourly_rate?: number;
  verification_status: 'pending' | 'approved' | 'flagged' | 'unverifiable';
  screenshot_id?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Screenshot {
  id: string;
  entry_id: string;
  file_path: string;
  file_size_bytes: number;
  file_format: 'jpeg' | 'png' | 'webp';
  verification_decision?: 'approved' | 'flagged' | 'unverifiable';
  verified_by_verifier_id?: string;
  verification_notes?: string;
  verified_at?: string;
  uploaded_at: string;
}

export interface GrievancePost {
  id: string;
  worker_id?: string;
  platform: string;
  category: string;
  title: string;
  description: string;
  is_anonymous: boolean;
  tags: string[];
  escalation_state: 'open' | 'escalated' | 'resolved';
  upvote_count: number;
  created_at: string;
  updated_at: string;
}

export interface GrievanceComment {
  id: string;
  post_id: string;
  user_id: string;
  comment_text: string;
  is_from_advocate: boolean;
  created_at: string;
}

export interface OTPToken {
  id: string;
  email: string;
  token: string;
  purpose: 'verify_email' | 'reset_password';
  expiry: string;
  is_used: boolean;
  created_at: string;
}

export interface PasswordResetToken {
  id: string;
  user_id: string;
  token: string;
  expiry: string;
  is_used: boolean;
  created_at: string;
}
