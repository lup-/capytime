export interface ScheduleParams {
  enabled?: boolean;
  price?: string;
  days?: number[];
  timeFrom?: string;
  timeTo?: string;
  breakNeeded?: boolean;
  breakDuration?: string;
  slotDuration?: number;
}

export interface Psychologist {
  id?: string;
  firstName?: string;
  lastName?: string;
  slug?: string;
  specialty?: string;
  avatar?: string;
  online?: ScheduleParams;
  offline?: ScheduleParams;
  offlineAddress?: string;
  timezone?: string;
  videoLink?: string;
  videoConferenceMode?: "per_booking" | "single";
  about?: string;
  education?: string;
  proExperience?: string;
  problems?: string[];
  googleCalendarConnected?: boolean;
  yandexTelemostConnected?: boolean;
}

export interface PsychologistUpdateRequest extends Psychologist {
  send_email?: boolean;
}

export interface Specialty {
  label: string;
  value: string;
}
